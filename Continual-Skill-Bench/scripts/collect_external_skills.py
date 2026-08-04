#!/usr/bin/env python3
"""
Collect external open-source skills and normalize into local JSONL format.

Supported sources:
1) GitHub repository (scan markdown/json files by path patterns)
2) Direct URL (raw markdown/json pages)
3) SkillHub API search (keyword + pagination)

Output schema (one JSON object per line):
  skill_name, skill_summary, when_to_use, inputs, steps, validation, tags, source

Usage:
  python3 collect_external_skills.py \
    --manifest /home/wyd/datasets/skillsbench/scripts/external_skill_sources.json \
    --output /home/wyd/datasets/skillsbench/scripts/open_source_skills.jsonl

Environment:
  GITHUB_TOKEN (optional): increases GitHub API limits.
  SKILLHUB_API_KEY (optional): for skillhub_api sources.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_INCLUDE_PATTERNS = [
    "**/SKILL.md",
    "**/skill.md",
    "**/*skill*.md",
    "**/.cursor/skills/**/*.md",
    "**/skills/**/*.md",
    "**/*skill*.json",
]


def http_get(url: str, token: str | None = None, timeout: int = 30) -> str:
    headers = {"User-Agent": "skillsbench-collector/1.0"}
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def http_get_with_retry(url: str, token: str | None, timeout: int, retries: int) -> str:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return http_get(url, token=token, timeout=timeout)
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(min(2.0 * (attempt + 1), 6.0))
    if last_error is not None:
        raise last_error
    raise RuntimeError("unreachable")


def http_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> Any:
    req_headers = {"User-Agent": "skillsbench-collector/1.0", "Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    data: bytes | None = None
    if payload is not None:
        req_headers.setdefault("Content-Type", "application/json")
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, headers=req_headers, method=method.upper(), data=data)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def http_json_with_retry(
    url: str,
    method: str,
    headers: dict[str, str] | None,
    payload: dict[str, Any] | None,
    timeout: int,
    retries: int,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return http_json(url=url, method=method, headers=headers, payload=payload, timeout=timeout)
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(min(2.0 * (attempt + 1), 6.0))
    if last_error is not None:
        raise last_error
    raise RuntimeError("unreachable")


def normalize_slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "external-skill"


def extract_bullets(section_text: str) -> list[str]:
    bullets: list[str] = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^[-*]\s+", line):
            bullets.append(re.sub(r"^[-*]\s+", "", line).strip())
        elif re.match(r"^\d+\.\s+", line):
            bullets.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return bullets


def split_md_sections(md: str) -> tuple[str, dict[str, str]]:
    lines = md.splitlines()
    title = ""
    sections: dict[str, list[str]] = {}
    current = "_intro"
    sections[current] = []

    for line in lines:
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line)
        if m:
            heading = m.group(1).strip()
            key = heading.lower()
            if not title:
                title = heading
            current = key
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)

    joined = {k: "\n".join(v).strip() for k, v in sections.items()}
    return title, joined


def first_paragraph(text: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not parts:
        return ""
    first = re.sub(r"\s+", " ", parts[0]).strip()
    return first[:260]


def tags_from_text(*chunks: str) -> list[str]:
    text = " ".join(chunks).lower()
    vocab = [
        "finance", "economics", "macro", "market", "valuation", "risk", "derivatives",
        "fixed-income", "document-qa", "python", "excel", "csv", "pdf", "web", "api",
    ]
    return [t for t in vocab if t in text]


def normalize_skill(skill: dict[str, Any], source: str) -> dict[str, Any]:
    name = skill.get("skill_name") or skill.get("name") or skill.get("title") or "external-skill"
    summary = skill.get("skill_summary") or skill.get("summary") or skill.get("description") or ""
    when_to_use = skill.get("when_to_use") or skill.get("use_case") or ""
    inputs = skill.get("inputs") or []
    steps = skill.get("steps") or []
    validation = skill.get("validation") or skill.get("checks") or []
    tags = skill.get("tags") or []

    out = {
        "skill_name": normalize_slug(str(name)),
        "skill_summary": str(summary).strip() or "Reusable external skill.",
        "when_to_use": str(when_to_use).strip() or "Use when task matches this workflow.",
        "inputs": [str(x).strip() for x in inputs if str(x).strip()],
        "steps": [str(x).strip() for x in steps if str(x).strip()],
        "validation": [str(x).strip() for x in validation if str(x).strip()],
        "tags": [str(x).strip().lower() for x in tags if str(x).strip()],
        "source": source,
    }

    if not out["inputs"]:
        out["inputs"] = ["task prompt", "relevant data/files", "expected output format"]
    if not out["steps"]:
        out["steps"] = [
            "Interpret task objective and constraints.",
            "Extract or gather required evidence.",
            "Compute or reason step-by-step.",
            "Return final answer in required format.",
        ]
    if not out["validation"]:
        out["validation"] = [
            "Outputs are internally consistent.",
            "Evidence supports each claim.",
            "Format constraints are satisfied.",
        ]
    return out


def parse_skill_markdown(md: str, source: str, fallback_name: str) -> dict[str, Any]:
    title, sections = split_md_sections(md)
    intro = sections.get("_intro", "")

    name = title or fallback_name
    summary = first_paragraph(intro)
    if not summary:
        summary = first_paragraph(md)

    when_to_use = ""
    for k in sections:
        if any(x in k for x in ("when to use", "use when", "trigger", "applicability")):
            when_to_use = first_paragraph(sections[k])
            break

    inputs: list[str] = []
    steps: list[str] = []
    validation: list[str] = []

    for k, body in sections.items():
        lk = k.lower()
        bullets = extract_bullets(body)
        if not bullets:
            continue
        if any(x in lk for x in ("input", "prerequisite", "requirement", "context")):
            inputs.extend(bullets)
        elif any(x in lk for x in ("step", "workflow", "instruction", "procedure", "process")):
            steps.extend(bullets)
        elif any(x in lk for x in ("validation", "check", "test", "verify", "quality")):
            validation.extend(bullets)

    return normalize_skill(
        {
            "skill_name": name,
            "skill_summary": summary,
            "when_to_use": when_to_use,
            "inputs": inputs,
            "steps": steps,
            "validation": validation,
            "tags": tags_from_text(name, summary, when_to_use, source),
        },
        source=source,
    )


def parse_skill_json(text: str, source: str, fallback_name: str) -> list[dict[str, Any]]:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return []

    rows: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        if any(k in obj for k in ("skill_name", "name", "summary", "steps")):
            rows.append(normalize_skill(obj, source=source))
        elif "skills" in obj and isinstance(obj["skills"], list):
            for item in obj["skills"]:
                if isinstance(item, dict):
                    rows.append(normalize_skill(item, source=source))
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                rows.append(normalize_skill(item, source=source))

    if not rows:
        rows.append(
            normalize_skill(
                {"skill_name": fallback_name, "skill_summary": "External JSON content parsed as one skill."},
                source=source,
            )
        )
    return rows


def github_list_files(repo: str, branch: str, token: str | None, timeout: int, retries: int) -> list[str]:
    url = f"https://api.github.com/repos/{repo}/git/trees/{urllib.parse.quote(branch, safe='')}?recursive=1"
    raw = http_get_with_retry(url, token=token, timeout=timeout, retries=retries)
    payload = json.loads(raw)
    tree = payload.get("tree", [])
    return [item.get("path", "") for item in tree if item.get("type") == "blob" and item.get("path")]


def github_raw_url(repo: str, branch: str, path: str) -> str:
    safe_branch = urllib.parse.quote(branch, safe="")
    safe_path = "/".join(urllib.parse.quote(p, safe="") for p in path.split("/"))
    return f"https://raw.githubusercontent.com/{repo}/{safe_branch}/{safe_path}"


def should_include(path: str, patterns: list[str]) -> bool:
    unix_path = path.replace("\\", "/")
    return any(fnmatch.fnmatch(unix_path, p) for p in patterns)


def collect_from_github_repo(
    source: dict[str, Any], token: str | None, timeout: int, retries: int
) -> list[dict[str, Any]]:
    repo = source["repo"]
    branch = source.get("branch", "main")
    include = source.get("include") or DEFAULT_INCLUDE_PATTERNS
    max_files = int(source.get("max_files", 200))

    files = github_list_files(repo=repo, branch=branch, token=token, timeout=timeout, retries=retries)
    selected = [p for p in files if should_include(p, include)]
    selected = selected[:max_files]

    skills: list[dict[str, Any]] = []
    for path in selected:
        raw_url = github_raw_url(repo, branch, path)
        src = f"github:{repo}/{path}"
        try:
            text = http_get_with_retry(raw_url, token=None, timeout=timeout, retries=retries)
        except urllib.error.URLError:
            continue

        fname = Path(path).name.lower()
        fallback = Path(path).stem
        if fname.endswith(".md"):
            skills.append(parse_skill_markdown(text, source=src, fallback_name=fallback))
        elif fname.endswith(".json"):
            skills.extend(parse_skill_json(text, source=src, fallback_name=fallback))
    return skills


def collect_from_url(source: dict[str, Any], timeout: int, retries: int) -> list[dict[str, Any]]:
    url = source["url"]
    name = source.get("name") or Path(urllib.parse.urlparse(url).path).stem or "url-skill"
    src = f"url:{url}"
    text = http_get_with_retry(url, token=None, timeout=timeout, retries=retries)

    lower = url.lower()
    if lower.endswith(".json"):
        return parse_skill_json(text, source=src, fallback_name=name)
    return [parse_skill_markdown(text, source=src, fallback_name=name)]


def dedupe_skills(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    for s in skills:
        by_name.setdefault(s["skill_name"], s)
    return sorted(by_name.values(), key=lambda x: x["skill_name"])


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def pick_list(payload: Any, candidate_keys: list[str]) -> list[dict[str, Any]]:
    """
    Extract first list-like field from common API response shapes.
    Supports:
      - top-level list
      - {"data":[...]} / {"items":[...]} / {"results":[...]} / {"skills":[...]}
      - {"data":{"items":[...]}} style nesting
    """
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []

    for k in candidate_keys:
        v = payload.get(k)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        for k in candidate_keys:
            v = data.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    return []


def collect_from_skillhub_api(
    source: dict[str, Any], api_key: str | None, timeout: int, retries: int
) -> list[dict[str, Any]]:
    """
    Collect skills from SkillHub-like APIs.

    Expected source config:
    {
      "type": "skillhub_api",
      "base_url": "https://www.skillhub.club/api/v1",
      "search_path": "/skills/search",          # optional
      "query": "finance economics",             # optional
      "category": "Data",                       # optional
      "page_size": 50,                          # optional
      "max_pages": 5,                           # optional
      "method": "POST"                          # optional, default POST
    }
    """
    base_url = str(source.get("base_url", "https://www.skillhub.club/api/v1")).rstrip("/")
    search_path = str(source.get("search_path", "/skills/search"))
    method = str(source.get("method", "POST")).upper()
    query = str(source.get("query", "finance economics")).strip()
    category = source.get("category")
    page_size = int(source.get("page_size", 50))
    max_pages = int(source.get("max_pages", 5))

    # Common auth header patterns used by public API docs.
    headers: dict[str, str] = {}
    if api_key:
        headers["x-api-key"] = api_key
        headers["Authorization"] = f"Bearer {api_key}"

    all_rows: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        payload: dict[str, Any] = {
            "query": query,
            "page": page,
            "pageSize": page_size,
            "limit": page_size,
            "offset": (page - 1) * page_size,
        }
        if category:
            payload["category"] = category

        url = f"{base_url}{search_path}"
        if method == "GET":
            qs = urllib.parse.urlencode(payload)
            resp = http_json_with_retry(
                f"{url}?{qs}",
                method="GET",
                headers=headers,
                payload=None,
                timeout=timeout,
                retries=retries,
            )
        else:
            resp = http_json_with_retry(
                url,
                method="POST",
                headers=headers,
                payload=payload,
                timeout=timeout,
                retries=retries,
            )

        items = pick_list(resp, ["items", "results", "skills", "data"])
        if not items:
            break

        for item in items:
            # Normalize with tolerant field mapping from typical marketplace APIs.
            name = item.get("skill_name") or item.get("slug") or item.get("name") or item.get("title") or "skillhub-skill"
            summary = (
                item.get("skill_summary")
                or item.get("summary")
                or item.get("description")
                or item.get("intro")
                or ""
            )
            when_to_use = item.get("when_to_use") or item.get("use_case") or item.get("trigger") or ""
            steps = as_list(item.get("steps")) or as_list(item.get("workflow"))
            inputs = as_list(item.get("inputs")) or as_list(item.get("input_schema"))
            validation = as_list(item.get("validation")) or as_list(item.get("checks"))
            tags = as_list(item.get("tags")) or as_list(item.get("categories"))

            item_source_id = item.get("id") or item.get("slug") or item.get("skill_id") or ""
            src = f"skillhub:{base_url}{search_path}"
            if item_source_id:
                src = f"{src}#{item_source_id}"

            all_rows.append(
                normalize_skill(
                    {
                        "skill_name": name,
                        "skill_summary": summary,
                        "when_to_use": when_to_use,
                        "inputs": inputs,
                        "steps": steps,
                        "validation": validation,
                        "tags": tags or tags_from_text(str(name), str(summary), str(when_to_use)),
                    },
                    source=src,
                )
            )

        # Stop early on short page.
        if len(items) < page_size:
            break

    return all_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect and normalize external open-source skills.")
    parser.add_argument("--manifest", required=True, help="Path to source manifest JSON.")
    parser.add_argument(
        "--output",
        default="/home/wyd/datasets/skillsbench/scripts/open_source_skills.jsonl",
        help="Output normalized skills JSONL path.",
    )
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds per request.")
    parser.add_argument("--retries", type=int, default=1, help="Retry count for each HTTP request.")
    parser.add_argument(
        "--source-types",
        nargs="*",
        default=[],
        help="Only run these source types, e.g. skillhub_api github_repo url",
    )
    parser.add_argument(
        "--only-source-indexes",
        nargs="*",
        default=[],
        help="Only run these 1-based source indexes from manifest, e.g. 4 5",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise ValueError("Manifest must be a JSON array.")

    gh_token = os.environ.get("GITHUB_TOKEN")
    skillhub_key = os.environ.get("SKILLHUB_API_KEY")
    collected: list[dict[str, Any]] = []
    selected_types = {x.strip() for x in args.source_types if str(x).strip()}
    selected_indexes: set[int] = set()
    for raw_idx in args.only_source_indexes:
        try:
            selected_indexes.add(int(raw_idx))
        except ValueError:
            pass

    for idx, src in enumerate(manifest, start=1):
        if not isinstance(src, dict):
            continue
        src_type = src.get("type")
        if selected_types and src_type not in selected_types:
            continue
        if selected_indexes and idx not in selected_indexes:
            continue
        try:
            if src_type == "github_repo":
                rows = collect_from_github_repo(
                    src,
                    token=gh_token,
                    timeout=args.timeout,
                    retries=args.retries,
                )
            elif src_type == "url":
                rows = collect_from_url(src, timeout=args.timeout, retries=args.retries)
            elif src_type == "skillhub_api":
                # Allow key from env or source["api_key"].
                rows = collect_from_skillhub_api(
                    src,
                    api_key=str(src.get("api_key") or skillhub_key or ""),
                    timeout=args.timeout,
                    retries=args.retries,
                )
            else:
                print(f"[WARN] source #{idx}: unknown type={src_type}, skipped")
                continue
            collected.extend(rows)
            print(f"[OK] source #{idx} ({src_type}) -> {len(rows)} skills")
        except Exception as e:
            print(f"[WARN] source #{idx} failed: {e}")

    normalized = dedupe_skills(collected)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in normalized:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved {len(normalized)} normalized skills to {out_path}")


if __name__ == "__main__":
    main()

