#!/usr/bin/env python3
"""
简单测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.project_manager import ProjectManager

pm = ProjectManager()

print("创建项目...")
project = pm.create_project("测试项目")

print("项目创建成功!")
print(f"项目名: {project.name}")
print(f"项目路径: {pm.get_project_path(project.name)}")

print("\n列出项目...")
projects = pm.list_projects()
for p in projects:
    print(f"  - {p}")

