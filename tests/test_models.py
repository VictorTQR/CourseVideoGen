import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.project import Slide, Project

def test_slide_new_fields():
    slide = Slide(id=1, image="a.png")
    assert slide.content == ""
    assert slide.script is None
    assert slide.audio is None
    assert slide.duration is None

def test_slide_with_content():
    slide = Slide(id=1, image="a.png", content="Python 简介")
    assert slide.content == "Python 简介"

def test_project_with_overview():
    overview = {"course_summary": "test", "slide_overview": []}
    project = Project(name="Test", slides=[], overview=overview)
    assert project.overview == overview

def test_from_dict_migration_old_format():
    """旧格式只有 script 没有 content，应迁移"""
    data = {
        "name": "Test",
        "slides": [{"id": 1, "image": "a.png", "script": "old script"}],
        "created_at": "", "updated_at": ""
    }
    project = Project.from_dict(data)
    assert project.slides[0].content == "old script"
    assert project.slides[0].script is None

def test_from_dict_migration_new_format():
    """新格式有 content 和 script"""
    data = {
        "name": "Test",
        "slides": [{"id": 1, "image": "a.png", "content": "raw", "script": "oral"}],
        "created_at": "", "updated_at": ""
    }
    project = Project.from_dict(data)
    assert project.slides[0].content == "raw"
    assert project.slides[0].script == "oral"

def test_project_round_trip():
    """测试 to_dict -> from_dict 往返"""
    project = Project(
        name="Test",
        slides=[Slide(id=1, image="a.png", content="Hi")],
        overview={"course_summary": "test", "slide_overview": []}
    )
    restored = Project.from_dict(project.to_dict())
    assert restored.name == project.name
    assert restored.slides[0].content == project.slides[0].content
    assert restored.slides[0].script is None
    assert restored.overview == project.overview
