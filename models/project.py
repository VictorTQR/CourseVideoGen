"""
项目数据模型
"""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Slide:
    """单页 PPT 数据"""
    id: int
    image: str  # 图片文件名
    script: str = ""  # 讲解稿
    audio: Optional[str] = None  # 音频文件名
    duration: float = 3.0  # 显示时长（秒）


@dataclass
class Project:
    """项目数据"""
    name: str
    slides: List[Slide]
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "slides": [asdict(slide) for slide in self.slides],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Project":
        slides = [Slide(**s) for s in data["slides"]]
        return cls(
            name=data["name"],
            slides=slides,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

