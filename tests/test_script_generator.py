import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch, MagicMock
from models.project import Project, Slide
from core.script_generator import generate_overview, generate_scripts
from core.llm import LLMConfig

@pytest.fixture
def sample_project():
    return Project(
        name="Python入门课",
        slides=[
            Slide(id=1, image="s1.png", content="Python 简介\n- 通用语言\n- 简单易学"),
            Slide(id=2, image="s2.png", content="变量与数据类型\n- 整数\n- 字符串"),
        ]
    )

def test_generate_overview_returns_dict(sample_project):
    """测试 generate_overview 返回 dict 并写入 project.overview"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    mock_response = '{"course_summary": "test", "target_audience": "beginners", "tone": "easy", "slide_overview": []}'

    with patch("core.script_generator.call_llm", return_value=mock_response):
        overview = generate_overview(sample_project, config)

        assert "course_summary" in overview
        assert sample_project.overview == overview

def test_generate_overview_calls_llm_with_all_slides(sample_project):
    """测试 generate_overview 将所有 slide content 发送给 LLM"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    mock_response = '{"course_summary": "test", "slide_overview": []}'

    with patch("core.script_generator.call_llm", return_value=mock_response) as mock_call:
        generate_overview(sample_project, config)

        call_args = mock_call.call_args
        user_text = call_args[0][1]
        assert "Python入门课" in user_text
        assert "---第1页---" in user_text
        assert "---第2页---" in user_text
        assert "Python 简介" in user_text

def test_generate_scripts_returns_file_paths(sample_project, tmp_path):
    """测试 generate_scripts 返回文件路径列表"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}

    with patch("core.script_generator.call_llm", return_value="这是一段讲解稿"):
        paths = generate_scripts(sample_project, config, str(tmp_path))

        assert len(paths) == 2
        assert "slide_01.txt" in os.path.basename(paths[0])
        assert "slide_02.txt" in os.path.basename(paths[1])

def test_generate_scripts_writes_to_files(sample_project, tmp_path):
    """测试 generate_scripts 正确写入 txt 文件"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}

    with patch("core.script_generator.call_llm", return_value="口语化讲解稿内容"):
        generate_scripts(sample_project, config, str(tmp_path))

        for i in range(1, 3):
            filepath = os.path.join(str(tmp_path), "scripts", f"slide_0{i}.txt")
            assert os.path.exists(filepath)
            with open(filepath, encoding="utf-8") as f:
                assert f.read() == "口语化讲解稿内容"

def test_generate_scripts_updates_slide_script(sample_project, tmp_path):
    """测试 generate_scripts 自动回写 slide.script"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}

    with patch("core.script_generator.call_llm", return_value="讲解稿文本"):
        generate_scripts(sample_project, config, str(tmp_path))

        assert sample_project.slides[0].script == "讲解稿文本"
        assert sample_project.slides[1].script == "讲解稿文本"

def test_generate_scripts_retry_on_failure(sample_project, tmp_path):
    """测试 generate_scripts 失败时重试一次"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}

    slide_idx = [-1]

    def mock_call(*args, **kwargs):
        slide_idx[0] += 1
        if slide_idx[0] == 0:
            raise Exception("API Error")
        return "成功"

    with patch("core.script_generator.call_llm", side_effect=mock_call):
        with patch("builtins.print") as mock_print:
            paths = generate_scripts(sample_project, config, str(tmp_path))

            assert len(paths) == 2
            assert slide_idx[0] == 2
            mock_print.assert_any_call("[WARN] 第 1 页生成失败，重试中...")

def test_generate_scripts_continues_on_failure(sample_project, tmp_path):
    """测试单页失败不影响其他页"""
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}

    slide1_attempts = [0]

    def mock_call(*args, **kwargs):
        slide1_attempts[0] += 1
        if slide1_attempts[0] <= 2:
            raise Exception("API Error")
        return "讲解稿"

    with patch("core.script_generator.call_llm", side_effect=mock_call):
        with patch("builtins.print") as mock_print:
            paths = generate_scripts(sample_project, config, str(tmp_path))

            assert len(paths) == 1
            assert "slide_02.txt" in os.path.basename(paths[0])
            assert slide1_attempts[0] == 3