"""
音频生成模块 - 使用 Edge-TTS
"""

import os
import asyncio
import edge_tts
from typing import Optional


class AudioGenerator:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.audios_dir = os.path.join(project_dir, "audios")

    async def generate_audio(
        self,
        text: str,
        output_filename: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
    ) -> tuple[str, float]:
        """
        生成音频

        Args:
            text: 讲解文本
            output_filename: 输出文件名
            voice: 发音人
            rate: 语速

        Returns:
            (audio_path, duration_seconds)
        """
        output_path = os.path.join(self.audios_dir, output_filename)

        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

        # 获取音频时长
        duration = self._get_audio_duration(output_path)

        return output_path, duration

    def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长（秒）"""
        try:
            from mutagen.mp3 import MP3

            audio = MP3(audio_path)
            return audio.info.length
        except Exception as e:
            print(f"[WARN] mutagen 获取时长失败: {e}")
            try:
                from moviepy.editor import AudioFileClip

                with AudioFileClip(audio_path) as audio:
                    return audio.duration
            except Exception as e2:
                print(f"[WARN] moviepy 也失败: {e2}")
                # 估算：大概每秒 5 个汉字
                return 1.0

    @staticmethod
    def list_voices() -> list:
        """列出可用的发音人（中文）"""
        return [
            "zh-CN-XiaoxiaoNeural",  # 女声
            "zh-CN-YunxiNeural",  # 男声
            "zh-CN-YunyangNeural",  # 男声
            "zh-CN-XiaoyiNeural",  # 女声
            "zh-HK-HiuMaanNeural",  # 粤语
            "zh-TW-HsiaoChenNeural",  # 台湾腔
        ]
