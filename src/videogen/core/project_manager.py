"""
项目管理模块
"""
import os
import json
import shutil
from datetime import datetime
from typing import Optional
from videogen.models.project import Project, Slide


class ProjectManager:
    def __init__(self, base_dir: str = "workspace"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def get_project_path(self, project_name: str) -> str:
        return os.path.join(self.base_dir, project_name)

    def create_project(self, project_name: str) -> Project:
        """创建新项目"""
        project_path = self.get_project_path(project_name)
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "slides"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "audios"), exist_ok=True)

        now = datetime.now().isoformat()
        project = Project(
            name=project_name,
            slides=[],
            created_at=now,
            updated_at=now
        )
        self._save_project(project)
        return project

    def load_project(self, project_name: str) -> Optional[Project]:
        """加载项目"""
        project_path = self.get_project_path(project_name)
        json_path = os.path.join(project_path, "project.json")
        if not os.path.exists(json_path):
            return None
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Project.from_dict(data)

    def reset_project(self, project: Project):
        """重置项目数据（重新导入前调用）

        清空 slides/scripts/audios 目录和 output.mp4，
        重置 project.json 中的 slides 和 overview，
        保留 name、created_at。
        """
        project_path = self.get_project_path(project.name)
        for subdir in ("slides", "scripts", "audios"):
            dir_path = os.path.join(project_path, subdir)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)
        output_path = os.path.join(project_path, "output.mp4")
        if os.path.exists(output_path):
            os.remove(output_path)

        project.slides = []
        project.overview = None
        self._save_project(project)

    def _save_project(self, project: Project):
        """保存项目到文件"""
        project.updated_at = datetime.now().isoformat()
        project_path = self.get_project_path(project.name)
        json_path = os.path.join(project_path, "project.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)

    def add_slide(self, project: Project, image_filename: str) -> Slide:
        """添加一页 PPT"""
        slide_id = len(project.slides) + 1
        slide = Slide(
            id=slide_id,
            image=image_filename,
            content="",
            script=None,
            duration=None
        )
        project.slides.append(slide)
        self._save_project(project)
        return slide

    def update_slide_content(self, project: Project, slide_id: int, content: str):
        """更新 content 字段（import 阶段用）"""
        for slide in project.slides:
            if slide.id == slide_id:
                slide.content = content
                self._save_project(project)
                return
        raise ValueError(f"Slide {slide_id} not found")

    def apply_slide_script(self, project: Project, slide_id: int, script: str):
        """应用讲解稿（script apply 阶段用）"""
        for slide in project.slides:
            if slide.id == slide_id:
                slide.script = script
                self._save_project(project)
                return
        raise ValueError(f"Slide {slide_id} not found")

    def update_overview(self, project: Project, overview: dict):
        """更新课程概览"""
        project.overview = overview
        self._save_project(project)

    def update_slide_audio(self, project: Project, slide_id: int, audio_filename: str, duration: float):
        """更新音频信息"""
        for slide in project.slides:
            if slide.id == slide_id:
                slide.audio = audio_filename
                slide.duration = duration
                self._save_project(project)
                return
        raise ValueError(f"Slide {slide_id} not found")

    def list_projects(self) -> list:
        """列出所有项目，返回项目摘要列表"""
        result = []
        for name in os.listdir(self.base_dir):
            path = os.path.join(self.base_dir, name)
            json_path = os.path.join(path, "project.json")
            if os.path.isdir(path) and os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                result.append(data)
        return sorted(result, key=lambda x: x.get("name", ""))

