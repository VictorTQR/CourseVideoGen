"""Core Package"""
from .project_manager import ProjectManager
from .ppt_parser import PPTParser
from .audio_generator import AudioGenerator
from .video_generator import VideoGenerator
from .html_generator import HTMLSlideGenerator, HTMLSlideRenderer

__all__ = [
    "ProjectManager",
    "PPTParser",
    "AudioGenerator",
    "VideoGenerator",
    "HTMLSlideGenerator",
    "HTMLSlideRenderer"
]
