#!/usr/bin/env python3
"""
CourseVideoGen - PPT 讲解视频自动生成工具

使用方法:
    python main.py create "我的项目"
    python main.py import-ppt "lesson.pptx"
    python main.py generate-audio
    python main.py generate-video
    python main.py run-all
"""

import os
import sys
import asyncio
import argparse

# 把当前目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.project_manager import ProjectManager
from core.ppt_parser import PPTParser
from core.audio_generator import AudioGenerator
from core.video_generator import VideoGenerator
from core.html_generator import HTMLSlideGenerator, HTMLSlideRenderer


class CourseVideoGen:
    def __init__(self):
        self.pm = ProjectManager()
        self.current_project = None
        self.project_dir = None

    def create(self, project_name: str):
        """创建新项目"""
        print(f"[CREATE] 创建项目: {project_name}")
        self.current_project = self.pm.create_project(project_name)
        self.project_dir = self.pm.get_project_path(project_name)
        print(f"[OK] 项目已创建: {self.project_dir}")

    def load(self, project_name: str):
        """加载已有项目"""
        print(f"[LOAD] 加载项目: {project_name}")
        self.current_project = self.pm.load_project(project_name)
        if not self.current_project:
            print(f"[ERROR] 项目不存在: {project_name}")
            sys.exit(1)
        self.project_dir = self.pm.get_project_path(project_name)
        print(f"[OK] 已加载 {len(self.current_project.slides)} 页")

    def import_ppt(self, pptx_path: str):
        """导入 PPT"""
        if not self.current_project:
            print("[ERROR] 请先创建或加载项目")
            sys.exit(1)

        print(f"[IMPORT] 导入 PPT: {pptx_path}")
        parser = PPTParser(self.project_dir)

        # 转换为图片
        images = parser.ppt_to_images(pptx_path)

        # 添加到项目
        for image in images:
            self.pm.add_slide(self.current_project, image)

        # 同时提取文本，保存到 scripts 目录作参考
        slide_texts = parser.get_slide_text(pptx_path)
        scripts_dir = os.path.join(self.project_dir, "scripts")
        for i, text in enumerate(slide_texts):
            script_path = os.path.join(scripts_dir, f"slide_{i + 1:02d}.txt")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(text)
            # 更新到 slide 的 script 字段
            if i < len(self.current_project.slides):
                self.pm.update_slide_script(self.current_project, i + 1, text)

        print(f"[OK] 成功导入 {len(images)} 页")

    def import_html(
        self, json_path: str, theme: str = "light", template: str = "default"
    ):
        """从 JSON 导入 HTML 幻灯片"""
        if not self.current_project:
            print("❌ 请先创建或加载项目")
            sys.exit(1)

        print(f"📥 导入 HTML 幻灯片: {json_path} (模板: {template})")

        # 1. 生成 HTML
        html_gen = HTMLSlideGenerator(self.project_dir)
        html_path = html_gen.generate_from_json(json_path, template)

        # 2. 渲染为图片
        renderer = HTMLSlideRenderer(self.project_dir)
        images = renderer.render_to_images(html_path)

        if not images:
            print("[ERROR] HTML 渲染失败")
            return

        # 3. 添加到项目
        for image in images:
            self.pm.add_slide(self.current_project, image)

        # 4. 生成空的讲解稿模板
        scripts_dir = os.path.join(self.project_dir, "scripts")
        import json

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        slides_data = data.get("slides", [])
        for i, slide_data in enumerate(slides_data):
            script_path = os.path.join(scripts_dir, f"slide_{i + 1:02d}.txt")
            # 尝试从 JSON 获取讲解稿，或用标题作为默认
            script = slide_data.get("script", f"{slide_data.get('title', '')}")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)
            if i < len(self.current_project.slides):
                self.pm.update_slide_script(self.current_project, i + 1, script)

        print(f"[OK] 成功导入 {len(images)} 页 HTML 幻灯片")

    def list_templates(self):
        """列出所有可用模板"""
        html_gen = HTMLSlideGenerator(self.project_dir if self.project_dir else ".")
        templates = html_gen.list_available_templates()
        print("[TEMPLATES] 可用模板:")
        for t in templates:
            print(f"  - {t}")

    async def generate_audio(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        """生成音频"""
        if not self.current_project:
            print("[ERROR] 请先加载项目")
            sys.exit(1)

        print(f"[AUDIO] 生成音频 (发音人: {voice})...")
        audio_gen = AudioGenerator(self.project_dir)

        for slide in self.current_project.slides:
            if not slide.script.strip():
                print(f"[WARN] 第 {slide.id} 页没有讲解稿，跳过")
                continue

            print(f"   生成第 {slide.id} 页...")
            audio_filename = f"audio_{slide.id:02d}.mp3"
            audio_path, duration = await audio_gen.generate_audio(
                slide.script, audio_filename, voice=voice
            )
            self.pm.update_slide_audio(
                self.current_project, slide.id, audio_filename, duration
            )

        print("[OK] 音频生成完成")

    def generate_video(self, output_filename: str = "output.mp4"):
        """生成视频"""
        if not self.current_project:
            print("[ERROR] 请先加载项目")
            sys.exit(1)

        print("[VIDEO] 生成视频...")
        video_gen = VideoGenerator(self.project_dir)
        output_path = os.path.join(self.project_dir, output_filename)

        video_gen.generate_final_video(self.current_project.slides, output_path)

        print(f"[OK] 视频已生成: {output_path}")

    def list(self):
        """列出所有项目"""
        projects = self.pm.list_projects()
        if not projects:
            print("暂无项目")
            return
        print("[LIST] 项目列表:")
        for p in projects:
            print(f"  - {p}")


def main():
    parser = argparse.ArgumentParser(
        description="CourseVideoGen - PPT 讲解视频自动生成工具"
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # create
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("name", help="项目名称")

    # load
    load_parser = subparsers.add_parser("load", help="加载项目")
    load_parser.add_argument("name", help="项目名称")

    # import-ppt
    import_parser = subparsers.add_parser("import-ppt", help="导入 PPT")
    import_parser.add_argument("file", help="PPTX 文件路径")
    import_parser.add_argument("--project", help="项目名称（如不指定使用当前）")

    # import-html
    import_html_parser = subparsers.add_parser(
        "import-html", help="从 JSON 导入 HTML 幻灯片"
    )
    import_html_parser.add_argument("file", help="JSON 配置文件路径")
    import_html_parser.add_argument("--theme", help="主题: light/dark", default="light")
    import_html_parser.add_argument("--template", help="模板名称", default="default")
    import_html_parser.add_argument("--project", help="项目名称（如不指定使用当前）")

    # list-templates
    subparsers.add_parser("list-templates", help="列出所有可用模板")

    # generate-audio
    audio_parser = subparsers.add_parser("generate-audio", help="生成音频")
    audio_parser.add_argument("--project", help="项目名称")
    audio_parser.add_argument("--voice", help="发音人", default="zh-CN-XiaoxiaoNeural")

    # generate-video
    video_parser = subparsers.add_parser("generate-video", help="生成视频")
    video_parser.add_argument("--project", help="项目名称")
    video_parser.add_argument("--output", help="输出文件名", default="output.mp4")

    # run-all
    all_parser = subparsers.add_parser(
        "run-all", help="一键全部生成（需要先 import-ppt）"
    )
    all_parser.add_argument("--project", help="项目名称")
    all_parser.add_argument("--voice", help="发音人", default="zh-CN-XiaoxiaoNeural")
    all_parser.add_argument("--output", help="输出文件名", default="output.mp4")

    # list
    subparsers.add_parser("list", help="列出所有项目")

    args = parser.parse_args()

    app = CourseVideoGen()

    if args.command == "list":
        app.list()
    elif args.command == "create":
        app.create(args.name)
    elif args.command == "load":
        app.load(args.name)
    elif args.command == "import-ppt":
        if args.project:
            app.load(args.project)
        app.import_ppt(args.file)
    elif args.command == "import-html":
        if args.project:
            app.load(args.project)
        app.import_html(args.file, args.theme, args.template)
    elif args.command == "list-templates":
        app.list_templates()
    elif args.command == "generate-audio":
        if args.project:
            app.load(args.project)
        asyncio.run(app.generate_audio(args.voice))
    elif args.command == "generate-video":
        if args.project:
            app.load(args.project)
        app.generate_video(args.output)
    elif args.command == "run-all":
        if args.project:
            app.load(args.project)
        asyncio.run(app.generate_audio(args.voice))
        app.generate_video(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
