#!/usr/bin/env python3
"""
图片转视频工具 - 将多张图片按顺序展示生成视频

使用方法:
    # 所有图片使用相同时长
    python image_to_video.py --images img1.jpg img2.png img3.jpg --output video.mp4
    python image_to_video.py --images img1.jpg img2.jpg --output video.mp4 --duration 3
    python image_to_video.py --images img1.jpg img2.jpg --output video.mp4 --resolution 1920x1080
    
    # 每张图片单独指定时长（推荐）
    python image_to_video.py --images img1.jpg:2 img2.jpg:5 img3.png:3 --output video.mp4
"""

import argparse
import os
import sys
from PIL import Image
import numpy as np

try:
    from moviepy.editor import ImageClip, concatenate_videoclips
except ImportError:
    print("正在安装 moviepy...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy.editor import ImageClip, concatenate_videoclips


def create_image_video(image_entries, output_path, default_duration=3, resolution=None):
    """
    将多张图片拼接成视频
    
    Args:
        image_entries: 图片条目列表，格式可以是：
                      - ["img1.jpg", "img2.jpg"]  (使用默认时长)
                      - ["img1.jpg:2", "img2.jpg:5"]  (每张单独指定时长)
        output_path: 输出视频路径
        default_duration: 默认每张图片显示时长（秒）
        resolution: 目标分辨率 (width, height)，None 则使用第一张图片的尺寸
    """
    clips = []
    
    # 确定目标分辨率
    target_size = None
    if resolution:
        target_size = resolution
    
    for entry in image_entries:
        # 解析条目：支持 "path.jpg" 或 "path.jpg:duration"
        if ":" in entry:
            parts = entry.split(":")
            # 处理 Windows 盘符情况 (如 C:\image.jpg)
            if len(parts) > 2 and len(parts[0]) == 1 and entry[1] == ":":
                img_path = entry
                duration = default_duration
            else:
                img_path = ":".join(parts[:-1])
                try:
                    duration = float(parts[-1])
                except:
                    img_path = entry
                    duration = default_duration
        else:
            img_path = entry
            duration = default_duration
        
        if not os.path.exists(img_path):
            print(f"警告: 找不到文件 {img_path}，跳过")
            continue
            
        print(f"处理图片: {img_path} (显示 {duration} 秒)")
        
        # 创建图片剪辑
        clip = ImageClip(img_path).set_duration(duration)
        
        # 如果需要调整尺寸
        if target_size:
            clip = clip.resize(target_size)
            
        clips.append(clip)
    
    if not clips:
        print("错误: 没有有效的图片")
        return False
        
    # 拼接所有剪辑
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 导出视频
    print(f"正在生成视频: {output_path}")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac'
    )
    
    print(f"✅ 视频生成完成: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='图片转视频工具')
    parser.add_argument('--images', '-i', nargs='+', required=True,
                        help='图片文件路径列表')
    parser.add_argument('--output', '-o', required=True,
                        help='输出视频文件路径 (例如: output.mp4)')
    parser.add_argument('--duration', '-d', type=float, default=3,
                        help='默认每张图片显示时长（秒），默认: 3。'\
                             '也可以在图片路径后加 :duration 单独指定，如 img.jpg:5')
    parser.add_argument('--resolution', '-r', 
                        help='目标分辨率，例如: 1920x1080，默认使用第一张图片尺寸')
    
    args = parser.parse_args()
    
    # 解析分辨率
    resolution = None
    if args.resolution:
        try:
            w, h = map(int, args.resolution.split('x'))
            resolution = (w, h)
        except:
            print("错误: 分辨率格式不正确，应为 宽度x高度，例如 1920x1080")
            return 1
    
    # 执行生成
    success = create_image_video(
        args.images,
        args.output,
        args.duration,
        resolution
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

