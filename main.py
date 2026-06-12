#!/usr/bin/env python3
"""
CourseVideoGen - PPT 讲解视频自动生成工具

使用方法:
    cvg create "我的项目"
    cvg import-ppt "lesson.pptx" -p "我的项目"
    cvg import-html "slides.html" -p "我的项目"
    cvg script generate -p "我的项目"
    cvg generate-audio -p "我的项目"
    cvg run-all -p "我的项目"
"""

import os
import sys
import asyncio

from dotenv import load_dotenv
from loguru import logger
import typer

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.project_manager import ProjectManager
from core.ppt_parser import PPTParser
from core.audio_generator import AudioGenerator
from core.video_generator import VideoGenerator
from core.html_generator import HTMLSlideRenderer
from core.script_generator import generate_overview, generate_scripts
from core.llm import resolve_llm_config

app = typer.Typer(
    name="videogen",
    help="PPT 讲解视频自动生成工具",
    no_args_is_help=True,
)
script_app = typer.Typer(help="讲解稿相关命令", no_args_is_help=True)
app.add_typer(script_app, name="script")

pm = ProjectManager()


def _require_project(project_name: str):
    """加载项目，返回 (project, project_dir)。项目不存在则报错退出。"""
    project = pm.load_project(project_name)
    if not project:
        logger.error(f"项目不存在: {project_name}")
        logger.info('使用 cvg create "项目名" 创建')
        raise typer.Exit(1)
    project_dir = pm.get_project_path(project_name)
    return project, project_dir


@app.command()
def create(name: str = typer.Argument(help="项目名称")):
    """创建新项目。"""
    logger.info(f"创建项目: {name}")
    project = pm.create_project(name)
    project_dir = pm.get_project_path(name)
    logger.success(f"项目已创建: {project_dir}")


@app.command("list")
def list_projects():
    """列出所有项目。"""
    projects = pm.list_projects()
    if not projects:
        logger.info("暂无项目")
        return
    logger.info("项目列表:")
    for p in projects:
        logger.info(f"  - {p['name']} ({len(p['slides'])} 页, 更新: {p['updated_at']})")


@app.command("import-ppt")
def import_ppt(
    file: str = typer.Argument(help="PPTX 文件路径"),
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
):
    """导入 PPTX 文件，渲染为图片并提取文本内容。"""
    logger.info(f"导入 PPT: {file}")
    proj, project_dir = _require_project(project)
    parser = PPTParser(project_dir)

    images = parser.ppt_to_images(file)
    for image in images:
        pm.add_slide(proj, image)

    slide_texts = parser.get_slide_text(file)
    for i, text in enumerate(slide_texts):
        if i < len(proj.slides):
            pm.update_slide_content(proj, i + 1, text)

    logger.success(f"成功导入 {len(images)} 页")


@app.command("import-html")
def import_html(
    file: str = typer.Argument(help="HTML 文件路径"),
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
):
    """导入 HTML 幻灯片文件，Playwright 截图并提取文本内容。"""
    logger.info(f"导入 HTML: {file}")
    proj, project_dir = _require_project(project)
    renderer = HTMLSlideRenderer(project_dir)

    images_and_texts = renderer.render_to_images(file)
    for image_filename, text_content in images_and_texts:
        slide = pm.add_slide(proj, image_filename)
        if text_content:
            pm.update_slide_content(proj, slide.id, text_content)

    logger.success(f"成功导入 {len(images_and_texts)} 页")


@script_app.command("generate")
def script_generate(
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
    model: str = typer.Option(None, "--model", help="LLM 模型"),
    base_url: str = typer.Option(None, "--base-url", help="API 基础地址"),
    api_key: str = typer.Option(None, "--api-key", help="API 密钥"),
):
    """LLM 生成讲解稿，自动回写 project.json。"""
    proj, project_dir = _require_project(project)
    if not proj.slides:
        logger.error("项目没有幻灯片，请先运行 import-ppt 或 import-html")
        raise typer.Exit(1)

    config = resolve_llm_config(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    logger.info("Phase 1: 生成课程概览...")
    overview = generate_overview(proj, config)
    pm.update_overview(proj, overview)
    logger.success("课程概览已保存")

    logger.info("Phase 2: 生成讲解稿...")
    scripts_map = generate_scripts(proj, config, project_dir)
    for slide_id, script_text in scripts_map.items():
        pm.apply_slide_script(proj, slide_id, script_text)
    logger.success(f"生成 {len(scripts_map)} 页讲解稿")
    logger.info("提示：查看 scripts/*.txt，如有需要可编辑后运行 script apply")


@script_app.command("apply")
def script_apply(
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
):
    """将 scripts/*.txt 中的讲解稿回写到 project.json。"""
    proj, project_dir = _require_project(project)
    import glob as glob_mod

    scripts_dir = os.path.join(project_dir, "scripts")
    if not os.path.exists(scripts_dir):
        logger.error("scripts 目录不存在，请先运行 script generate")
        raise typer.Exit(1)

    txt_files = sorted(glob_mod.glob(os.path.join(scripts_dir, "slide_*.txt")))
    if not txt_files:
        logger.error("scripts 目录为空，请先运行 script generate")
        raise typer.Exit(1)

    applied = 0
    for txt_path in txt_files:
        basename = os.path.basename(txt_path)
        slide_id = int(basename.split("_")[1].split(".")[0])
        with open(txt_path, "r", encoding="utf-8") as f:
            script_text = f.read()
        if script_text.strip():
            pm.apply_slide_script(proj, slide_id, script_text.strip())
            applied += 1
    logger.success(f"已回写 {applied} 页讲解稿")


@app.command("generate-audio")
def generate_audio(
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
    voice: str = typer.Option("zh-CN-XiaoxiaoNeural", "--voice", help="发音人"),
    rate: str = typer.Option("+0%", "--rate", help="语速"),
):
    """为每页讲解稿生成语音。"""
    proj, project_dir = _require_project(project)
    logger.info(f"生成音频 (voice={voice}, rate={rate})")
    generator = AudioGenerator(project_dir)

    async def _gen():
        for slide in proj.slides:
            if not slide.script:
                logger.warning(f"跳过第 {slide.id} 页 (无讲解稿)")
                continue
            logger.info(f"生成第 {slide.id}/{len(proj.slides)} 页...")
            audio_file = f"audio_{slide.id:02d}.mp3"
            audio_path, duration = await generator.generate_audio(
                slide.script, audio_file, voice, rate
            )
            pm.update_slide_audio(proj, slide.id, audio_file, duration)
            logger.success(f"第 {slide.id} 页完成 ({duration:.1f}s)")

    asyncio.run(_gen())
    logger.success("音频生成完成")


@app.command("generate-video")
def generate_video(
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
    output: str = typer.Option("output.mp4", "--output", "-o", help="输出文件名"),
):
    """将图片和音频合成为视频。"""
    proj, project_dir = _require_project(project)
    logger.info(f"生成视频: {output}")
    generator = VideoGenerator(project_dir)
    output_path = os.path.join(project_dir, output)
    generator.generate_final_video(proj.slides, output_path)
    logger.success(f"视频已生成: {output_path}")


@app.command("run-all")
def run_all(
    project: str = typer.Option(..., "--project", "-p", help="项目名称"),
    output: str = typer.Option("output.mp4", "--output", "-o", help="输出文件名"),
    voice: str = typer.Option("zh-CN-XiaoxiaoNeural", "--voice", help="发音人"),
    rate: str = typer.Option("+0%", "--rate", help="语速"),
):
    """一键生成音频和视频。"""
    proj, project_dir = _require_project(project)
    logger.info(f"生成音频 (voice={voice}, rate={rate})")
    generator = AudioGenerator(project_dir)

    async def _gen():
        for slide in proj.slides:
            if not slide.script:
                logger.warning(f"跳过第 {slide.id} 页 (无讲解稿)")
                continue
            logger.info(f"生成第 {slide.id}/{len(proj.slides)} 页...")
            audio_file = f"audio_{slide.id:02d}.mp3"
            audio_path, duration = await generator.generate_audio(
                slide.script, audio_file, voice, rate
            )
            pm.update_slide_audio(proj, slide.id, audio_file, duration)
            logger.success(f"第 {slide.id} 页完成 ({duration:.1f}s)")

    asyncio.run(_gen())
    logger.success("音频生成完成")

    logger.info(f"生成视频: {output}")
    vgen = VideoGenerator(project_dir)
    output_path = os.path.join(project_dir, output)
    vgen.generate_final_video(proj.slides, output_path)
    logger.success(f"视频已生成: {output_path}")


if __name__ == "__main__":
    app()
