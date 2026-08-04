#!/usr/bin/env python3
"""调试脚本：检查网站 HTML 结构"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

print("=" * 70)
print("🔍 调试 SkillsBench 任务页面")
print("=" * 70)

# 1. 尝试用 requests
print("\n1️⃣ 使用 requests 获取页面...")
try:
    resp = requests.get("https://www.skillsbench.ai/tasks", timeout=10)
    soup_requests = BeautifulSoup(resp.content, "html.parser")
    
    # 查找所有链接
    links = soup_requests.find_all("a")
    print(f"✅ 找到 {len(links)} 个链接")
    
    # 查找任务相关的链接
    task_links = [l for l in links if "/tasks/" in l.get("href", "")]
    print(f"📍 任务相关链接: {len(task_links)} 个")
    
    if task_links[:3]:
        print("\n前 3 个任务链接:")
        for link in task_links[:3]:
            print(f"  - {link.get('href')}")
            print(f"    文本: {link.text.strip()}")
    
    # 检查页面大小
    print(f"\n📄 页面大小: {len(resp.text)} 字节")
    
    # 查找可能的任务容器
    divs = soup_requests.find_all("div", class_=True)
    print(f"📦 div 元素: {len(divs)} 个")
    
    # 看是否有特定的 class
    classes = set()
    for div in divs:
        for cls in div.get("class", []):
            classes.add(cls)
    
    print(f"\n🏷️ 前 20 个 CSS class:")
    for cls in sorted(list(classes))[:20]:
        print(f"   - {cls}")
    
except Exception as e:
    print(f"❌ 错误: {e}")

# 2. 用 Playwright
print("\n" + "=" * 70)
print("2️⃣ 使用 Playwright 获取渲染后的页面...")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("⏳ 加载页面...")
        page.goto("https://www.skillsbench.ai/tasks", wait_until="domcontentloaded")
        
        print("⏳ 等待动态内容加载...")
        import time
        for i in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(2)
        
        content = page.content()
        soup_playwright = BeautifulSoup(content, "html.parser")
        
        print(f"✅ 页面大小: {len(content)} 字节")
        
        # 查找任务链接
        links = soup_playwright.find_all("a")
        task_links = [l for l in links if "/tasks/" in l.get("href", "")]
        
        print(f"📍 任务相关链接: {len(task_links)} 个")
        
        if task_links:
            print("\n前 5 个任务:")
            for i, link in enumerate(task_links[:5], 1):
                href = link.get("href", "")
                text = link.text.strip()
                print(f"\n{i}. {text}")
                print(f"   URL: {href}")
        else:
            print("\n❌ 未找到任务链接")
            
            # 保存 HTML 以供检查
            with open("debug_output.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("\n💾 完整页面已保存到 debug_output.html")
        
        browser.close()
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70 + "\n")
