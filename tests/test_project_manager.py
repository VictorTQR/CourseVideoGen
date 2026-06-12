import pytest
import os
import sys
import tempfile
import importlib.util

spec = importlib.util.spec_from_file_location("project_manager", "core/project_manager.py")
pm_module = importlib.util.module_from_spec(spec)
sys.modules['core.project_manager'] = pm_module
spec.loader.exec_module(pm_module)
ProjectManager = pm_module.ProjectManager

@pytest.fixture
def pm(tmp_path):
    return ProjectManager(base_dir=str(tmp_path))

def test_add_slide_initializes_new_fields(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    slide = project.slides[0]
    assert slide.content == ""
    assert slide.script is None
    assert slide.duration is None

def test_update_slide_content(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    pm.update_slide_content(project, 1, "Python 简介")
    assert project.slides[0].content == "Python 简介"

def test_apply_slide_script(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    pm.apply_slide_script(project, 1, "口服讲解稿")
    assert project.slides[0].script == "口服讲解稿"

def test_update_overview(pm):
    project = pm.create_project("test")
    overview = {"course_summary": "test"}
    pm.update_overview(project, overview)
    assert project.overview == overview

def test_update_slide_content_invalid_id(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    with pytest.raises(ValueError, match="Slide 99 not found"):
        pm.update_slide_content(project, 99, "content")

def test_apply_slide_script_invalid_id(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    with pytest.raises(ValueError, match="Slide 99 not found"):
        pm.apply_slide_script(project, 99, "script")