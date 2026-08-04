#!/usr/bin/env python3
"""
爬虫脚本：从 https://www.skillsbench.ai/tasks 抓取 science 相关任务

依赖：
  pip install requests beautifulsoup4 selenium playwright

使用方式：
  python scrape_science_tasks.py [--output FILE] [--driver {requests,selenium,playwright}]

输出：
  - science_tasks.json: JSON 格式任务列表
  - science_tasks.csv: CSV 格式任务列表
  - science_tasks.md: Markdown 格式任务列表
"""

import json
import csv
import os
import sys
import time
import argparse
import re
from typing import List, Dict, Optional, Iterable
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

SCRIPT_DIR = Path(__file__).resolve().parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 需要安装依赖: pip install requests beautifulsoup4")
    exit(1)


class ScienceTaskScraper:
    """Science 任务爬虫"""

    DIFFICULTY_VALUES = {"easy", "medium", "hard"}
    DEFAULT_SOURCES = [
        "skillsbench",
        "scienceagentbench",
        "labbench2",
        "labbench",
        "scibench",
        "astabench",
    ]
    SOURCE_URLS = {
        "skillsbench": "https://www.skillsbench.ai/tasks",
        "scienceagentbench": "https://huggingface.co/datasets/osunlp/ScienceAgentBench",
        "scienceagentbench_project": "https://osu-nlp-group.github.io/ScienceAgentBench/",
        "labbench2": "https://huggingface.co/datasets/EdisonScientific/labbench2",
        "labbench2_github": "https://github.com/EdisonScientific/labbench2",
        "labbench": "https://huggingface.co/datasets/futurehouse/lab-bench",
        "astabench": "https://huggingface.co/datasets/allenai/asta-bench",
        "astabench_project": "https://allenai.org/asta/bench",
        "astabench_github": "https://github.com/allenai/asta-bench",
        "scibench": "https://github.com/mandyyyyii/scibench/tree/main/dataset/original",
        "scibench_project": "https://scibench-ucla.github.io/",
    }
    LAB_BENCH_CONFIGS = [
        "CloningScenarios",
        "DbQA",
        "FigQA",
        "LitQA2",
        "ProtocolQA",
        "SeqQA",
        "SuppQA",
        "TableQA",
    ]
    SCIBENCH_DOMAIN_BY_FILE = {
        "atkins": "chemistry",
        "calculus": "mathematics",
        "chemmc": "chemistry",
        "class": "physics",
        "diff": "mathematics",
        "fund": "physics",
        "matter": "physics",
        "quan": "physics",
        "stat": "mathematics",
        "thermo": "physics",
    }
    ASTABENCH_PUBLIC_TASK_FILES = [
        "tasks/arxivdigestables/final_val_set.jsonl",
        "tasks/arxivdigestables/final_test_set.jsonl",
        "tasks/discoverybench/DBDev_w_hypothesis.json",
        "tasks/discoverybench/DBTest_w_hypothesis.json",
        "tasks/e2e_discovery/dev_may_2025.json",
        "tasks/e2e_discovery/test_may_2025.json",
        "tasks/e2e_discovery/dev_hard_jun_2025.json",
        "tasks/e2e_discovery/test_hard_jun_2025.json",
        "tasks/library_diagnostic/dev.jsonl",
        "tasks/library_diagnostic/test.jsonl",
        "tasks/paper_finder_bench/validation_2025_05.json",
        "tasks/paper_finder_bench/test_2025_05.json",
    ]

    # Science 相关关键词
    SCIENCE_KEYWORDS = {
        "biology": "生物学",
        "chemistry": "化学",
        "physics": "物理",
        "geology": "地质学",
        "astronomy": "天文学",
        "materials_science": "材料科学",
        "seismology": "地震学",
        "geophysics": "地球物理",
        "crystallography": "晶体学",
        "earth-science": "地球科学",
        "quantum": "量子",
        "protein": "蛋白质",
        "dna": "DNA",
        "gene": "基因",
        "crystal": "晶体",
        "earthquake": "地震",
        "gravitational": "引力",
        "exoplanet": "系外行星",
        "lake": "湖泊",
        "climate": "气候",
        "wave": "波",
    }

    BASE_URL = "https://www.skillsbench.ai"
    TASKS_PAGE = f"{BASE_URL}/tasks"
    
    # 不同方法对应的用户代理
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def __init__(
        self,
        output_dir: str = ".",
        driver: str = "playwright",
        headless: bool = True,
        sources: Optional[List[str]] = None,
        hf_token: Optional[str] = None,
    ):
        """
        初始化爬虫

        Args:
            output_dir: 输出目录
            driver: 使用的驱动 ('requests', 'selenium', 'playwright')
            headless: 是否使用无头模式
            sources: 要抓取的来源
            hf_token: Hugging Face token，用于 gated 数据集
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.driver = driver
        self.headless = headless
        self.sources = sources or list(self.DEFAULT_SOURCES)
        self.hf_token = hf_token
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self.tasks: List[Dict] = []
        self.source_status: Dict[str, str] = {}

    def _normalize_text(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value if v is not None)
        return re.sub(r"\s+", " ", str(value)).strip()

    def _truncate(self, text: str, limit: int = 500) -> str:
        text = self._normalize_text(text)
        if len(text) <= limit:
            return text
        return text[: limit - 3].rstrip() + "..."

    def _make_task(
        self,
        *,
        benchmark: str,
        task_id: str,
        title: str,
        description: str = "",
        difficulty: str = "",
        category: str = "",
        tags: Optional[Iterable[str] | str] = None,
        url: str = "",
        source_url: str = "",
        github_url: str = "",
    ) -> Dict:
        if isinstance(tags, str):
            tag_text = tags
        else:
            seen_tags = set()
            tag_values = []
            for tag in tags or []:
                tag_value = self._normalize_text(tag)
                if not tag_value or tag_value in seen_tags:
                    continue
                seen_tags.add(tag_value)
                tag_values.append(tag_value)
            tag_text = ", ".join(tag_values)

        return {
            "benchmark": benchmark,
            "title": self._truncate(self._normalize_text(title) or self._normalize_text(task_id), 160),
            "description": self._truncate(description),
            "difficulty": self._normalize_text(difficulty).lower() or "unknown",
            "category": self._normalize_text(category),
            "tags": tag_text,
            "task_id": self._normalize_text(task_id),
            "url": url or source_url,
            "source_url": source_url or url,
            "github_url": github_url,
            "scraped_time": datetime.now().isoformat(),
        }

    def _hf_headers(self) -> Dict[str, str]:
        if not self.hf_token:
            return {}
        return {"Authorization": f"Bearer {self.hf_token}"}

    def _get_json(self, url: str, *, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        response = self.session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def is_science_task(self, task_info: Dict) -> bool:
        """检查任务是否属于science领域"""
        content = " ".join([
            task_info.get("title", "").lower(),
            task_info.get("description", "").lower(),
            task_info.get("tags", "").lower(),
            task_info.get("category", "").lower(),
        ])

        # 检查关键词
        for keyword in self.SCIENCE_KEYWORDS.keys():
            pattern = rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?![a-z0-9])"
            if re.search(pattern, content):
                return True

        return False

    def scrape_with_requests(self) -> List[Dict]:
        """使用 requests 爬取（简单快速）"""
        print(f"📥 正在用 requests 爬取: {self.TASKS_PAGE}")
        
        try:
            response = self.session.get(self.TASKS_PAGE, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            tasks = self._parse_tasks_from_html(soup)
            print(f"✅ 成功爬取 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            return []

    def scrape_with_playwright(self) -> List[Dict]:
        """使用 Playwright 爬取（支持 JavaScript 渲染）"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ 需要安装 Playwright: pip install playwright && playwright install")
            return []

        print(f"📥 正在用 Playwright 爬取: {self.TASKS_PAGE}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(self.TASKS_PAGE, wait_until="domcontentloaded")
                
                # 等待页面加载
                time.sleep(3)
                
                # 滚动加载更多内容
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    time.sleep(1)
                
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                tasks = self._parse_tasks_from_html(soup)
                
                browser.close()
                print(f"✅ 成功爬取 {len(tasks)} 个任务")
                return tasks
                
        except Exception as e:
            print(f"❌ Playwright 爬取失败: {e}")
            return []

    def scrape_with_selenium(self) -> List[Dict]:
        """使用 Selenium 爬取"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
        except ImportError:
            print("❌ 需要安装 Selenium: pip install selenium")
            return []

        print(f"📥 正在用 Selenium 爬取: {self.TASKS_PAGE}")
        
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            
            driver = webdriver.Chrome(options=options)
            driver.get(self.TASKS_PAGE)
            
            # 等待任务卡片加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "task-card"))
            )
            
            # 滚动加载更多
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, window.innerHeight)")
                time.sleep(1)
            
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            tasks = self._parse_tasks_from_html(soup)
            
            driver.quit()
            print(f"✅ 成功爬取 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            print(f"❌ Selenium 爬取失败: {e}")
            return []

    def _parse_tasks_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """从 HTML 中解析任务信息"""
        tasks = []
        
        # 寻找任务链接（只包括 /tasks/ 的链接，排除 github.com）
        task_links = soup.find_all("a", {"href": re.compile(r"^/tasks/[a-z0-9-]+$")})
        
        seen_ids = set()
        for link in task_links:
            try:
                task_info = self._extract_task_info(link)
                if task_info:
                    task_id = task_info.get("task_id", "")
                    # 避免重复
                    if task_id and task_id not in seen_ids:
                        seen_ids.add(task_id)
                        # 检查是否是 science 任务
                        if self.is_science_task(task_info):
                            tasks.append(task_info)
            except Exception as e:
                # 跳过解析失败的任务
                continue
        
        return tasks

    def _find_task_card(self, link_element):
        """找到包含任务完整信息的卡片容器。"""
        candidate = None
        node = link_element

        for _ in range(8):
            node = node.parent
            if not node:
                break

            class_names = " ".join(node.get("class", []))
            text_content = node.get_text(" ", strip=True).lower()

            if node.find("p") and any(
                re.search(rf"\b{difficulty}\b", text_content)
                for difficulty in self.DIFFICULTY_VALUES
            ):
                candidate = node

            if "bg-card" in class_names and "text-card-foreground" in class_names:
                return node

        return candidate or link_element.find_parent(["div", "article", "section"])

    def _find_element_with_classes(self, container, tag_name: str, class_names: List[str]):
        """查找同时包含多个 class 的元素。"""
        if not container:
            return None

        for elem in container.find_all(tag_name):
            elem_classes = elem.get("class", [])
            if all(class_name in elem_classes for class_name in class_names):
                return elem

        return None

    def _extract_card_metadata(self, card, title: str) -> Dict[str, object]:
        """从任务卡片中提取领域、难度、标签和描述。"""
        description = ""
        difficulty = ""
        category = ""
        tags = []

        if not card:
            return {
                "description": description,
                "difficulty": difficulty,
                "category": category,
                "tags": tags,
            }

        desc_elem = card.find("p")
        description = desc_elem.get_text(" ", strip=True) if desc_elem else ""

        meta_container = self._find_element_with_classes(
            card,
            "div",
            ["gap-2", "flex-wrap", "items-center", "mt-2"],
        )
        if meta_container:
            for child in meta_container.find_all(["div", "span"], recursive=False):
                text = re.sub(r"\s+", " ", child.get_text(" ", strip=True)).strip()
                normalized = text.lower()
                if normalized in self.DIFFICULTY_VALUES:
                    difficulty = normalized
                elif text and text != title:
                    category = text

        seen_tags = set()
        for elem in card.find_all(["div", "span"]):
            elem_classes = elem.get("class", [])
            raw_text = re.sub(r"\s+", " ", elem.get_text(" ", strip=True)).strip()
            is_leaf_badge = not elem.find(["div", "span"])
            if "bg-secondary" not in elem_classes and not (
                raw_text.startswith("#") and is_leaf_badge
            ):
                continue

            tag = re.sub(r"^#\s*", "", raw_text).strip()
            if not tag or tag.lower() == "source" or re.match(r"^\+\s*\d+$", tag):
                continue

            if tag not in seen_tags:
                seen_tags.add(tag)
                tags.append(tag)

        if not difficulty:
            text_content = card.get_text(" ", strip=True).lower()
            for value in self.DIFFICULTY_VALUES:
                if re.search(rf"\b{value}\b", text_content):
                    difficulty = value
                    break

        return {
            "description": description,
            "difficulty": difficulty,
            "category": category,
            "tags": tags,
        }

    def _extract_task_info(self, link_element) -> Optional[Dict]:
        """从链接元素中提取任务信息"""
        try:
            # 从链接中获取基本信息
            task_id = link_element.get("href", "").split("/")[-1] if link_element.get("href") else ""
            title = link_element.text.strip() if link_element else ""
            
            if not task_id or not title or task_id == "tasks":
                return None
            
            # 查找任务卡片容器，获取更多信息
            parent = self._find_task_card(link_element)
            metadata = self._extract_card_metadata(parent, title)
            
            task_url = urljoin(self.BASE_URL, f"/tasks/{task_id}") if task_id else ""
            
            return self._make_task(
                benchmark="SkillsBench",
                title=title,
                description=metadata["description"],
                difficulty=metadata["difficulty"],
                category=metadata["category"],
                tags=metadata["tags"],
                task_id=task_id,
                url=task_url,
                source_url=self.SOURCE_URLS["skillsbench"],
                github_url=f"https://github.com/benchflow-ai/skillsbench/tree/main/tasks/{task_id}" if task_id else "",
            )
        except Exception as e:
            return None

    def _fetch_hf_rows(
        self,
        *,
        dataset: str,
        config: str,
        split: str = "train",
        page_size: int = 100,
    ) -> List[Dict]:
        """通过 Hugging Face datasets-server 分页获取公开或授权数据。"""
        rows = []
        offset = 0
        headers = self._hf_headers()

        while True:
            url = (
                "https://datasets-server.huggingface.co/rows"
                f"?dataset={dataset}&config={config}&split={split}&offset={offset}&length={page_size}"
            )
            response = None
            for attempt in range(5):
                response = self.session.get(url, headers=headers, timeout=60)
                if response.status_code not in {429, 502, 503, 504}:
                    break
                wait_seconds = 2 * (attempt + 1)
                print(f"⏳ Hugging Face 暂时不可用/限流，{wait_seconds}s 后重试: {config} offset={offset}")
                time.sleep(wait_seconds)

            if response is None:
                raise RuntimeError(f"请求失败: {url}")
            if response.status_code in {429, 502, 503, 504} and page_size > 20:
                page_size = max(20, page_size // 2)
                print(f"📉 缩小分页到 {page_size} 后继续: {config} offset={offset}")
                continue
            if response.status_code in {401, 403}:
                raise PermissionError(response.text[:300])
            response.raise_for_status()
            payload = response.json()

            rows.extend(item.get("row", {}) for item in payload.get("rows", []))
            total = payload.get("num_rows_total", len(rows))
            offset += page_size
            if offset >= total or not payload.get("rows"):
                break

        return rows

    def scrape_scienceagentbench(self) -> List[Dict]:
        """抓取 ScienceAgentBench verified split。"""
        source = "scienceagentbench"
        print("📥 正在抓取 ScienceAgentBench: osunlp/ScienceAgentBench verified")

        try:
            rows = self._fetch_hf_rows(
                dataset="osunlp/ScienceAgentBench",
                config="default",
                split="verified",
                page_size=100,
            )
        except Exception as e:
            self.source_status[source] = f"跳过: {e}"
            print(f"⚠️  ScienceAgentBench 抓取失败: {e}")
            return []

        tasks = []
        for row in rows:
            task_id = str(row.get("instance_id", ""))
            tasks.append(
                self._make_task(
                    benchmark="ScienceAgentBench",
                    task_id=f"sab-{task_id}",
                    title=row.get("task_inst", "") or f"ScienceAgentBench task {task_id}",
                    description=row.get("task_inst", ""),
                    difficulty="unknown",
                    category=row.get("domain", ""),
                    tags=[row.get("subtask_categories", ""), row.get("github_name", "")],
                    url=self.SOURCE_URLS["scienceagentbench"],
                    source_url=self.SOURCE_URLS["scienceagentbench"],
                    github_url=self.SOURCE_URLS["scienceagentbench_project"],
                )
            )

        self.source_status[source] = f"成功: {len(tasks)} 条"
        print(f"✅ ScienceAgentBench: {len(tasks)} 条")
        return tasks

    def scrape_labbench2(self) -> List[Dict]:
        """抓取 LABBench2；该数据集通常需要 Hugging Face 授权。"""
        source = "labbench2"
        print("📥 正在抓取 LABBench2: EdisonScientific/labbench2")

        if not self.hf_token:
            message = "需要 HF_TOKEN 并在 Hugging Face 页面接受访问授权"
            self.source_status[source] = f"跳过: {message}"
            print(f"⚠️  LABBench2 跳过: {message}")
            return []

        try:
            split_payload = self._get_json(
                "https://datasets-server.huggingface.co/splits?dataset=EdisonScientific/labbench2",
                headers=self._hf_headers(),
                timeout=60,
            )
        except Exception as e:
            self.source_status[source] = f"跳过: {e}"
            print(f"⚠️  LABBench2 抓取失败: {e}")
            return []

        tasks = []
        for split_info in split_payload.get("splits", []):
            config = split_info.get("config")
            split = split_info.get("split", "train")
            if not config:
                continue
            try:
                rows = self._fetch_hf_rows(
                    dataset="EdisonScientific/labbench2",
                    config=config,
                    split=split,
                    page_size=100,
                )
            except Exception as e:
                print(f"⚠️  LABBench2/{config} 跳过: {e}")
                continue

            for i, row in enumerate(rows):
                task_id = row.get("id") or f"{config}-{i}"
                question = row.get("question") or row.get("prompt") or row.get("task") or ""
                tasks.append(
                    self._make_task(
                        benchmark="LABBench2",
                        task_id=f"labbench2-{config}-{task_id}",
                        title=question or f"LABBench2 {config} task {i}",
                        description=question,
                        difficulty=row.get("difficulty", "unknown"),
                        category=config,
                        tags=[row.get("subtask", ""), row.get("tag", "")],
                        url=self.SOURCE_URLS["labbench2"],
                        source_url=self.SOURCE_URLS["labbench2"],
                        github_url=self.SOURCE_URLS["labbench2_github"],
                    )
                )

        self.source_status[source] = f"成功: {len(tasks)} 条"
        print(f"✅ LABBench2: {len(tasks)} 条")
        return tasks

    def scrape_labbench_public(self) -> List[Dict]:
        """抓取 LAB-Bench 公共版，作为生物/生化方向的公开任务来源。"""
        source = "labbench"
        print("📥 正在抓取 LAB-Bench public: futurehouse/lab-bench")
        tasks = []

        for config in self.LAB_BENCH_CONFIGS:
            try:
                rows = self._fetch_hf_rows(
                    dataset="futurehouse/lab-bench",
                    config=config,
                    split="train",
                    page_size=100,
                )
            except Exception as e:
                print(f"⚠️  LAB-Bench/{config} 跳过: {e}")
                continue

            for i, row in enumerate(rows):
                task_id = row.get("id") or f"{config}-{i}"
                question = row.get("question", "")
                source_links = row.get("sources") or row.get("source") or ""
                tags = [row.get("subtask", ""), row.get("tag", "")]
                if source_links:
                    tags.append(source_links)
                tasks.append(
                    self._make_task(
                        benchmark="LAB-Bench",
                        task_id=f"labbench-{config}-{task_id}",
                        title=question or f"LAB-Bench {config} task {i}",
                        description=question,
                        difficulty="unknown",
                        category=f"biology/{config}",
                        tags=tags,
                        url=self.SOURCE_URLS["labbench"],
                        source_url=self.SOURCE_URLS["labbench"],
                        github_url="https://github.com/Future-House/LAB-Bench",
                    )
                )

        self.source_status[source] = f"成功: {len(tasks)} 条"
        print(f"✅ LAB-Bench public: {len(tasks)} 条")
        return tasks

    def scrape_scibench(self) -> List[Dict]:
        """抓取 SciBench 原始 JSON 题目。"""
        source = "scibench"
        print("📥 正在抓取 SciBench: GitHub dataset/original")

        try:
            items = self._get_json(
                "https://api.github.com/repos/mandyyyyii/scibench/contents/dataset/original",
                timeout=60,
            )
        except Exception as e:
            self.source_status[source] = f"跳过: {e}"
            print(f"⚠️  SciBench 抓取失败: {e}")
            return []

        tasks = []
        for item in items:
            name = item.get("name", "")
            if item.get("type") != "file" or not name.endswith(".json") or name.endswith("_sol.json"):
                continue

            subject = name[:-5]
            domain = self.SCIBENCH_DOMAIN_BY_FILE.get(subject, "science")
            try:
                rows = self._get_json(item["download_url"], timeout=60)
            except Exception as e:
                print(f"⚠️  SciBench/{name} 跳过: {e}")
                continue

            for i, row in enumerate(rows):
                problem_id = self._normalize_text(row.get("problemid")) or str(i)
                task_id = f"scibench-{subject}-{i}-{problem_id}".replace(" ", "")
                problem = row.get("problem_text", "")
                tasks.append(
                    self._make_task(
                        benchmark="SciBench",
                        task_id=task_id,
                        title=problem or f"SciBench {subject} {problem_id}",
                        description=problem,
                        difficulty="unknown",
                        category=domain,
                        tags=[subject, row.get("source", ""), row.get("unit", "")],
                        url=item.get("html_url") or self.SOURCE_URLS["scibench"],
                        source_url=self.SOURCE_URLS["scibench"],
                        github_url=item.get("html_url") or self.SOURCE_URLS["scibench"],
                    )
                )

        self.source_status[source] = f"成功: {len(tasks)} 条"
        print(f"✅ SciBench: {len(tasks)} 条")
        return tasks

    def _records_from_json_payload(self, payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ["data", "examples", "tasks", "instances", "records", "questions"]:
                if isinstance(payload.get(key), list):
                    return payload[key]
            return [payload]
        return []

    def scrape_astabench(self) -> List[Dict]:
        """抓取 AstaBench gated 数据；需要 Hugging Face 授权。"""
        source = "astabench"
        print("📥 正在抓取 AstaBench: allenai/asta-bench")

        if not self.hf_token:
            message = "需要 HF_TOKEN 并在 Hugging Face 页面接受访问授权"
            self.source_status[source] = f"跳过: {message}"
            print(f"⚠️  AstaBench 跳过: {message}")
            return []

        tasks = []
        headers = self._hf_headers()
        for path in self.ASTABENCH_PUBLIC_TASK_FILES:
            url = f"https://huggingface.co/datasets/allenai/asta-bench/resolve/main/{path}"
            try:
                response = self.session.get(url, headers=headers, timeout=60)
                if response.status_code in {401, 403}:
                    raise PermissionError(response.text[:300])
                response.raise_for_status()
            except Exception as e:
                print(f"⚠️  AstaBench/{path} 跳过: {e}")
                continue

            records = []
            if path.endswith(".jsonl"):
                for line in response.text.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            else:
                try:
                    records = self._records_from_json_payload(response.json())
                except json.JSONDecodeError:
                    records = []

            benchmark_part = path.split("/")[1]
            for i, row in enumerate(records):
                task_id = (
                    row.get("id")
                    or row.get("task_id")
                    or row.get("instance_id")
                    or row.get("qid")
                    or f"{benchmark_part}-{i}"
                )
                description = (
                    row.get("question")
                    or row.get("prompt")
                    or row.get("task")
                    or row.get("instruction")
                    or row.get("description")
                    or row.get("query")
                    or json.dumps(row, ensure_ascii=False)[:500]
                )
                difficulty = row.get("difficulty", "")
                if not difficulty and "hard" in path.lower():
                    difficulty = "hard"
                tasks.append(
                    self._make_task(
                        benchmark="AstaBench",
                        task_id=f"astabench-{benchmark_part}-{task_id}",
                        title=description or f"AstaBench {benchmark_part} task {i}",
                        description=description,
                        difficulty=difficulty or "unknown",
                        category=benchmark_part,
                        tags=[path],
                        url=self.SOURCE_URLS["astabench"],
                        source_url=self.SOURCE_URLS["astabench"],
                        github_url=self.SOURCE_URLS["astabench_github"],
                    )
                )

        self.source_status[source] = f"成功: {len(tasks)} 条"
        print(f"✅ AstaBench: {len(tasks)} 条")
        return tasks

    def scrape(self) -> List[Dict]:
        """执行爬取"""
        print(f"\n🚀 开始爬取 Science/Math/Bio/Chem 相关任务...")
        print(f"🔧 SkillsBench 驱动: {self.driver}")
        print(f"📚 来源: {', '.join(self.sources)}\n")

        all_tasks = []
        normalized_sources = [source.lower().strip() for source in self.sources]
        if "all" in normalized_sources:
            normalized_sources = list(self.DEFAULT_SOURCES)

        for source in normalized_sources:
            if source == "skillsbench":
                if self.driver == "requests":
                    tasks = self.scrape_with_requests()
                elif self.driver == "playwright":
                    tasks = self.scrape_with_playwright()
                elif self.driver == "selenium":
                    tasks = self.scrape_with_selenium()
                else:
                    print(f"❌ 未知驱动: {self.driver}")
                    tasks = []
                self.source_status[source] = f"成功: {len(tasks)} 条"
            elif source == "scienceagentbench":
                tasks = self.scrape_scienceagentbench()
            elif source == "labbench2":
                tasks = self.scrape_labbench2()
            elif source in {"labbench", "lab-bench"}:
                tasks = self.scrape_labbench_public()
            elif source == "scibench":
                tasks = self.scrape_scibench()
            elif source == "astabench":
                tasks = self.scrape_astabench()
            else:
                print(f"⚠️  未知来源，跳过: {source}")
                self.source_status[source] = "跳过: 未知来源"
                tasks = []

            all_tasks.extend(tasks)

        # 去重：同一 benchmark + task_id 保留一份。
        deduped = []
        seen = set()
        for task in all_tasks:
            key = (task.get("benchmark", ""), task.get("task_id", ""))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(task)

        self.tasks = deduped

        print(f"\n✨ 共找到 {len(self.tasks)} 个相关任务\n")
        return self.tasks

    def save_json(self, filename: Optional[str] = None) -> str:
        """保存为 JSON"""
        filename = filename or "science_tasks.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到 JSON: {filepath}")
        return str(filepath)

    def save_csv(self, filename: Optional[str] = None) -> str:
        """保存为 CSV"""
        filename = filename or "science_tasks.csv"
        filepath = self.output_dir / filename
        
        if not self.tasks:
            print("⚠️  没有数据可保存")
            return ""
        
        keys = self.tasks[0].keys()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.tasks)
        
        print(f"💾 已保存到 CSV: {filepath}")
        return str(filepath)

    def save_markdown(self, filename: Optional[str] = None) -> str:
        """保存为 Markdown"""
        filename = filename or "science_tasks.md"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# SkillsBench Science 领域任务\n\n")
            f.write(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总数**: {len(self.tasks)} 个任务\n\n")
            f.write("## 来源网址\n\n")
            for name, url in self.SOURCE_URLS.items():
                f.write(f"- **{name}**: {url}\n")
            f.write("\n")
            
            # 按来源和难度分组
            by_benchmark = {}
            for task in self.tasks:
                benchmark = task.get("benchmark") or "Unknown"
                by_benchmark.setdefault(benchmark, []).append(task)
            
            for benchmark, benchmark_tasks in sorted(by_benchmark.items()):
                f.write(f"## {benchmark} ({len(benchmark_tasks)} 个)\n\n")
                by_difficulty = {}
                for task in benchmark_tasks:
                    diff = task.get("difficulty") or "unknown"
                    by_difficulty.setdefault(diff, []).append(task)

                ordered_difficulties = ["easy", "medium", "hard", "unknown"]
                ordered_difficulties += sorted(set(by_difficulty) - set(ordered_difficulties))
                for difficulty in ordered_difficulties:
                    if difficulty not in by_difficulty:
                        continue
                    tasks = by_difficulty[difficulty]
                    f.write(f"### {difficulty.upper()} ({len(tasks)} 个)\n\n")

                    for task in tasks:
                        title = task.get("title", "")
                        description = task.get("description", "")[:180]
                        category = task.get("category", "")
                        tags = task.get("tags", "")
                        url = task.get("url", "")
                        github_url = task.get("github_url", "")

                        f.write(f"#### [{title}]({url})\n\n")
                        if description:
                            f.write(f"{description}...\n\n")
                        if category:
                            f.write(f"**领域**: {category}\n\n")
                        if tags:
                            f.write(f"**标签**: {tags}\n\n")
                        f.write(f"- [数据/网站]({url})\n")
                        if github_url:
                            f.write(f"- [GitHub/项目页]({github_url})\n")
                        f.write("\n")
        
        print(f"💾 已保存到 Markdown: {filepath}")
        return str(filepath)

    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 爬取摘要")
        print("=" * 60)
        
        if not self.tasks:
            print("❌ 没有找到任何 Science 相关任务")
            return
        
        print(f"✅ 总计: {len(self.tasks)} 个任务\n")
        print("来源状态:")
        for source, status in self.source_status.items():
            print(f"  - {source}: {status}")
        print()
        
        by_benchmark = {}
        for task in self.tasks:
            benchmark = task.get("benchmark", "Unknown")
            by_benchmark[benchmark] = by_benchmark.get(benchmark, 0) + 1

        print("来源分布:")
        for benchmark, count in sorted(by_benchmark.items()):
            print(f"  - {benchmark}: {count} 个")

        by_difficulty = {}
        for task in self.tasks:
            diff = task.get("difficulty") or "unknown"
            by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
        
        print("\n难度分布:")
        for diff, count in sorted(by_difficulty.items()):
            print(f"  - {diff}: {count} 个")
        
        print("\n前 5 个任务:")
        for i, task in enumerate(self.tasks[:5], 1):
            print(f"  {i}. {task['title']}")
            print(f"     URL: {task['url']}")
        
        if len(self.tasks) > 5:
            print(f"  ... 还有 {len(self.tasks) - 5} 个任务")
        
        print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="从 SkillsBench 网站爬取 Science 相关任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 Playwright 驱动（默认，支持 JS 渲染）
  python scrape_science_tasks.py

  # 使用 Playwright（支持 JS 渲染）
  python scrape_science_tasks.py --driver playwright

  # 指定输出目录
  python scrape_science_tasks.py --output ./data

  # 只抓 SciBench 和 LAB-Bench 公共版
  python scrape_science_tasks.py --sources scibench,labbench
  
  # 仅输出 JSON
  python scrape_science_tasks.py --format json
        """
    )
    
    parser.add_argument(
        "--output",
        default=str(SCRIPT_DIR),
        help="输出目录（默认: 当前目录）"
    )
    parser.add_argument(
        "--driver",
        choices=["requests", "selenium", "playwright"],
        default="playwright",
        help="使用的爬虫驱动（默认: playwright）"
    )
    parser.add_argument(
        "--format",
        choices=["all", "json", "csv", "markdown"],
        default="all",
        help="输出格式（默认: all）"
    )
    parser.add_argument(
        "--sources",
        default="all",
        help=(
            "逗号分隔的数据来源（默认: all）。可选: "
            "skillsbench, scienceagentbench, labbench2, labbench, scibench, astabench"
        )
    )
    parser.add_argument(
        "--hf-token",
        default=None,
        help="Hugging Face token；也可通过 HF_TOKEN 或 HUGGINGFACE_HUB_TOKEN 环境变量提供"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="使用无头浏览器（仅对 selenium/playwright 有效）"
    )
    
    args = parser.parse_args()
    
    # 创建爬虫
    scraper = ScienceTaskScraper(
        output_dir=args.output,
        driver=args.driver,
        headless=args.headless,
        sources=[source.strip() for source in args.sources.split(",") if source.strip()],
        hf_token=args.hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN"),
    )
    
    # 执行爬取
    tasks = scraper.scrape()
    
    if not tasks:
        print("❌ 没有爬取到任何任务")
        return 1
    
    # 保存结果
    if args.format in ["all", "json"]:
        scraper.save_json()
    if args.format in ["all", "csv"]:
        scraper.save_csv()
    if args.format in ["all", "markdown"]:
        scraper.save_markdown()
    
    # 打印摘要
    scraper.print_summary()
    
    return 0


if __name__ == "__main__":
    exit(main())
