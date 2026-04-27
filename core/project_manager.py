"""
项目管理模块
"""
import os
import json
from datetime import datetime
from typing import Optional
from models.project import Project, Slide


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
            script="",
            duration=3.0
        )
        project.slides.append(slide)
        self._save_project(project)
        return slide

    def update_slide_script(self, project: Project, slide_id: int, script: str):
        """更新讲解稿"""
        for slide in project.slides:
            if slide.id == slide_id:
                slide.script = script
                self._save_project(project)
                return

    def update_slide_audio(self, project: Project, slide_id: int, audio_filename: str, duration: float):
        """更新音频信息"""
        for slide in project.slides:
            if slide.id == slide_id:
                slide.audio = audio_filename
                slide.duration = duration
                self._save_project(project)
                return

    def list_projects(self) -> list:
        """列出所有项目"""
        projects = []
        for name in os.listdir(self.base_dir):
            path = os.path.join(self.base_dir, name)
            if os.path.isdir(path) and os.path.exists(os.path.join(path, "project.json")):
                projects.append(name)
        return sorted(projects)

