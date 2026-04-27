#!/usr/bin/env python3
"""
修复音频时长的脚本
"""

import os
import json
from mutagen.mp3 import MP3


def fix_duration(project_dir):
    """修复项目中的音频时长"""
    project_json = os.path.join(project_dir, "project.json")
    audios_dir = os.path.join(project_dir, "audios")

    if not os.path.exists(project_json):
        print(f"[ERROR] 找不到项目文件: {project_json}")
        return

    with open(project_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[INFO] 正在修复 {len(data['slides'])} 页幻灯片的时长...")

    for slide in data["slides"]:
        if slide.get("audio"):
            audio_path = os.path.join(audios_dir, slide["audio"])
            if os.path.exists(audio_path):
                try:
                    audio = MP3(audio_path)
                    duration = audio.info.length
                    print(
                        f"  第 {slide['id']} 页: {duration:.2f} 秒 (之前: {slide.get('duration', 0)})"
                    )
                    slide["duration"] = duration
                except Exception as e:
                    print(f"  [WARN] 第 {slide['id']} 页: 获取时长失败: {e}")

    with open(project_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[OK] 已更新 project.json")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python fix_duration.py <项目名称>")
        print("示例: python fix_duration.py 提示词基础")
        sys.exit(1)

    project_name = sys.argv[1]
    project_dir = os.path.join("workspace", project_name)

    if not os.path.exists(project_dir):
        print(f"[ERROR] 项目不存在: {project_dir}")
        sys.exit(1)

    fix_duration(project_dir)
