"""
视频生成模块
"""

import os
from typing import List


class VideoGenerator:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.slides_dir = os.path.join(project_dir, "slides")
        self.audios_dir = os.path.join(project_dir, "audios")

    def generate_silent_video(self, slides: list, output_path: str) -> str:
        """
        生成无音轨的视频

        Args:
            slides: Slide 对象列表
            output_path: 输出文件路径
        """
        from moviepy.editor import ImageClip, concatenate_videoclips

        clips = []

        for slide in slides:
            image_path = os.path.join(self.slides_dir, slide.image)
            if not os.path.exists(image_path):
                print(f"[WARN] 找不到图片: {image_path}")
                continue

            clip = ImageClip(image_path).set_duration(slide.duration)
            clips.append(clip)

        if not clips:
            raise Exception("没有有效的幻灯片")

        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )
        return output_path

    def merge_audio_video(self, slides: list, silent_video_path: str, output_path: str):
        """
        将音频合并到视频

        Args:
            slides: Slide 对象列表（含音频信息）
            silent_video_path: 无音轨的视频
            output_path: 最终输出
        """
        from moviepy.editor import AudioFileClip, concatenate_audioclips, VideoFileClip

        # 收集所有音频
        audio_clips = []
        for slide in slides:
            if slide.audio:
                audio_path = os.path.join(self.audios_dir, slide.audio)
                if os.path.exists(audio_path):
                    audio_clip = AudioFileClip(audio_path)
                    audio_clips.append(audio_clip)

        if not audio_clips:
            print("[WARN] 没有音频，直接复制视频")
            import shutil

            shutil.copy(silent_video_path, output_path)
            return

        # 拼接音频
        final_audio = concatenate_audioclips(audio_clips)

        # 混流到视频
        video = VideoFileClip(silent_video_path)
        final_video = video.set_audio(final_audio)

        final_video.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )

        # 关闭资源
        video.close()
        final_audio.close()
        for clip in audio_clips:
            clip.close()

    def generate_final_video(self, slides: list, output_path: str) -> str:
        """
        一步生成最终视频（图片 + 音频直接合成）

        这种方式不需要先生成无音视频
        """
        from moviepy.editor import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips,
            concatenate_audioclips,
        )

        clips = []
        audio_clips = []

        for slide in slides:
            image_path = os.path.join(self.slides_dir, slide.image)
            if not os.path.exists(image_path):
                continue

            # 确保使用正确的时长
            duration = slide.duration
            if slide.audio and abs(duration - 3.0) < 0.1:  # 如果还是默认的3秒左右
                audio_path = os.path.join(self.audios_dir, slide.audio)
                if os.path.exists(audio_path):
                    try:
                        from mutagen.mp3 import MP3

                        audio = MP3(audio_path)
                        duration = audio.info.length
                        print(
                            f"[INFO] 第 {slide.id} 页: 使用实际音频时长 {duration:.2f} 秒"
                        )
                    except Exception as e:
                        print(f"[WARN] 第 {slide.id} 页: 获取时长失败，使用默认值")

            clip = ImageClip(image_path).set_duration(duration)
            clips.append(clip)

            if slide.audio:
                audio_path = os.path.join(self.audios_dir, slide.audio)
                if os.path.exists(audio_path):
                    audio_clip = AudioFileClip(audio_path)
                    audio_clips.append(audio_clip)

        if not clips:
            raise Exception("没有有效的幻灯片")

        final_video = concatenate_videoclips(clips, method="compose")

        final_audio = None
        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_video = final_video.set_audio(final_audio)

        final_video.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )

        # 清理
        if final_audio:
            final_audio.close()
            for clip in audio_clips:
                clip.close()

        return output_path
