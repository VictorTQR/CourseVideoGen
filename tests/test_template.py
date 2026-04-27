#!/usr/bin/env python3
"""
测试模板功能
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.html_generator import HTMLSlideGenerator

# 测试模板列表
print("🎨 测试模板功能")
print("=" * 50)

html_gen = HTMLSlideGenerator("/tmp/test_project")
templates = html_gen.list_available_templates()
print("可用模板:", templates)

print("\n✅ 模板功能正常！")
print("\n使用方法:")
print("  python main.py list-templates")
print("  python main.py create \"课程\"")
print("  python main.py import-html example_slides.json --template minimal --project \"课程\"")
