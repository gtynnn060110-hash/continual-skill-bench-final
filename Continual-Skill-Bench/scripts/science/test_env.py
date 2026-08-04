#!/usr/bin/env python3
"""环境验证脚本"""

import sys
import platform

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

print("=" * 70)
print("🔍 环境验证报告")
print("=" * 70)

print(f"\n✅ Python 版本: {sys.version}")
print(f"✅ 操作系统: {platform.platform()}")

print("\n📦 依赖包检查:\n")

packages = {
    "requests": "HTTP 请求库",
    "bs4": "HTML/XML 解析器",
    "selenium": "Selenium 浏览器自动化",
    "playwright": "Playwright 浏览器自动化",
}

all_ok = True
for pkg_name, description in packages.items():
    try:
        __import__(pkg_name)
        print(f"  ✅ {pkg_name:20} - {description}")
    except ImportError:
        print(f"  ❌ {pkg_name:20} - {description}")
        all_ok = False

print("\n" + "=" * 70)

if all_ok:
    print("✨ 所有依赖已正确安装！")
    print("\n🚀 你可以现在运行爬虫脚本:")
    print("   python scripts/science/scrape_science_tasks.py --driver playwright")
    print("\n📚 支持的驱动选项:")
    print("   --driver playwright  (默认，支持 JavaScript)")
    print("   --driver requests    (最快，但可能漏掉 JS 渲染内容)")
    print("   --driver selenium    (传统方式)")
else:
    print("⚠️  某些依赖未安装，请运行:")
    print("   pip install requests beautifulsoup4 selenium playwright")

print("=" * 70 + "\n")
