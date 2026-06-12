#!/usr/bin/env python3
"""
CourseVideoGen - PPT 讲解视频自动生成工具

使用方法:
    python main.py create "我的项目"
    python main.py import-ppt "lesson.pptx"
    python main.py import-html "slides.html"
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
from core.html_generator import HTMLSlideRenderer


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

        # 提取文本，写入 slide.content
        slide_texts = parser.get_slide_text(pptx_path)
        for i, text in enumerate(slide_texts):
            if i < len(self.current_project.slides):
                self.pm.update_slide_content(self.current_project, i + 1, text)

        print(f"[OK] 成功导入 {len(images)} 页")

    def import_html(self, html_path: str):
        """从 HTML 文件导入幻灯片（渲染为图片）"""
        if not self.current_project:
            print("[ERROR] 请先创建或加载项目")
            sys.exit(1)

        print(f"[IMPORT] 导入 HTML: {html_path}")
        renderer = HTMLSlideRenderer(self.project_dir)

        # 渲染为图片（返回 Tuple）
        results = renderer.render_to_images(html_path)

        # 添加到项目
        for image_filename, text_content in results:
            self.pm.add_slide(self.current_project, image_filename)
            # 更新 content
            slide_id = len(self.current_project.slides)
            self.pm.update_slide_content(self.current_project, slide_id, text_content)

        print(f"[OK] 成功导入 {len(results)} 页")

    def generate_audio(self, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%"):
        """生成所有幻灯片的音频"""
        if not self.current_project:
            print("[ERROR] 请先创建或加载项目")
            sys.exit(1)

        print(f"[AUDIO] 生成音频 (voice={voice}, rate={rate})")
        generator = AudioGenerator(self.project_dir)

        async def _gen():
            for slide in self.current_project.slides:
                if not slide.script:
                    print(f"   跳过第 {slide.id} 页 (无讲解稿)")
                    continue
                print(f"   生成第 {slide.id}/{len(self.current_project.slides)} 页...")
                audio_file = f"audio_{slide.id:02d}.mp3"
                audio_path, duration = await generator.generate_audio(
                    slide.script, audio_file, voice, rate
                )
                self.pm.update_slide_audio(
                    self.current_project, slide.id, audio_file, duration
                )
                print(f"   ✓ 第 {slide.id} 页完成 ({duration:.1f}s)")

        asyncio.run(_gen())
        print(f"[OK] 音频生成完成")

    def generate_video(self, output: str = "output.mp4"):
        """生成视频"""
        if not self.current_project:
            print("[ERROR] 请先创建或加载项目")
            sys.exit(1)

        print(f"[VIDEO] 生成视频: {output}")
        generator = VideoGenerator(self.project_dir)
        output_path = os.path.join(self.project_dir, output)
        generator.generate_final_video(self.current_project.slides, output_path)
        print(f"[OK] 视频已生成: {output_path}")

    def run_all(self, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%", output: str = "output.mp4"):
        """一键生成音频和视频"""
        self.generate_audio(voice, rate)
        self.generate_video(output)

    def list_projects(self):
        """列出所有项目"""
        projects = self.pm.list_projects()
        if not projects:
            print("暂无项目")
            return
        print("项目列表:")
        for p in projects:
            print(f"  - {p['name']} ({len(p['slides'])} 页, 更新: {p['updated_at']})")


def main():
    parser = argparse.ArgumentParser(description="CourseVideoGen - PPT 讲解视频自动生成工具")
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="列出所有项目")

    # create
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("name", help="项目名称")

    # load
    load_parser = subparsers.add_parser("load", help="加载已有项目")
    load_parser.add_argument("name", help="项目名称")

    # import-ppt
    ppt_parser = subparsers.add_parser("import-ppt", help="导入 PPTX")
    ppt_parser.add_argument("file", help="PPTX 文件路径")

    # import-html
    html_parser = subparsers.add_parser("import-html", help="导入 HTML 幻灯片文件")
    html_parser.add_argument("file", help="HTML 文件路径")

    # generate-audio
    audio_parser = subparsers.add_parser("generate-audio", help="生成音频")
    audio_parser.add_argument("--project", help="项目名称")

    # generate-video
    video_parser = subparsers.add_parser("generate-video", help="生成视频")
    video_parser.add_argument("--project", help="项目名称")
    video_parser.add_argument("--output", default="output.mp4", help="输出文件名")

    # run-all
    run_parser = subparsers.add_parser("run-all", help="一键生成音频和视频")
    run_parser.add_argument("--project", help="项目名称")
    run_parser.add_argument("--output", default="output.mp4", help="输出文件名")

    # generate
    gen_parser = subparsers.add_parser("generate", help="generate-audio / generate-video 的快捷方式")
    gen_parser.add_argument("what", choices=["audio", "video"])
    gen_parser.add_argument("--project", help="项目名称")
    gen_parser.add_argument("--output", default="output.mp4", help="输出文件名")

    # script
    script_parser = subparsers.add_parser("script", help="script 相关命令")
    script_subparsers = script_parser.add_subparsers(dest="script_command")

    # script generate
    gen_script_parser = script_subparsers.add_parser("generate", help="生成讲解稿")
    gen_script_parser.add_argument("--model", help="LLM 模型")
    gen_script_parser.add_argument("--base-url", help="API 基础地址")
    gen_script_parser.add_argument("--api-key", help="API 密钥")
    gen_script_parser.add_argument("--project", help="项目名称")

    # script apply
    apply_script_parser = script_subparsers.add_parser("apply", help="应用讲解稿")
    apply_script_parser.add_argument("--project", help="项目名称")

    args = parser.parse_args()

    app = CourseVideoGen()

    if args.command == "list":
        app.list_projects()

    elif args.command == "create":
        app.create(args.name)

    elif args.command == "load":
        app.load(args.name)

    elif args.command == "import-ppt":
        if not app.current_project:
            print("[ERROR] 请先使用 create 加载项目，再导入 PPT")
            print('  python main.py create "项目名"')
            print('  python main.py import-ppt "lesson.pptx"')
            sys.exit(1)
        app.import_ppt(args.file)

    elif args.command == "import-html":
        app.import_html(args.file)

    elif args.command == "generate-audio":
        if args.project:
            app.load(args.project)
        app.generate_audio()

    elif args.command == "generate-video":
        if args.project:
            app.load(args.project)
        app.generate_video(args.output)

    elif args.command == "run-all":
        if args.project:
            app.load(args.project)
        app.run_all(args.output)

    elif args.command == "generate":
        if args.project:
            app.load(args.project)
        if args.what == "audio":
            app.generate_audio()
        else:
            app.generate_video(args.output)

    elif args.command == "script":
        if args.script_command is None:
            script_parser.print_help()
        elif args.script_command == "generate":
            if args.project:
                app.load(args.project)
            if not app.current_project:
                print("[ERROR] 请先创建或加载项目")
                sys.exit(1)
            from core.llm import resolve_llm_config
            from core.script_generator import generate_overview, generate_scripts
            llm_config = resolve_llm_config(
                api_key=args.api_key,
                base_url=args.base_url,
                model=args.model
            )
            generate_overview(app.current_project, llm_config)
            generate_scripts(app.current_project, llm_config, app.project_dir)
            print("[OK] 讲解稿生成完成")
        elif args.script_command == "apply":
            if args.project:
                app.load(args.project)
            if not app.current_project:
                print("[ERROR] 请先创建或加载项目")
                sys.exit(1)
            scripts_dir = os.path.join(app.project_dir, "scripts")
            if not os.path.exists(scripts_dir):
                print("[ERROR] scripts 目录不存在，请先运行 script generate")
                sys.exit(1)
            import glob
            txt_files = sorted(glob.glob(os.path.join(scripts_dir, "slide_*.txt")))
            applied = 0
            for txt_path in txt_files:
                basename = os.path.basename(txt_path)
                # slide_01.txt -> 1
                slide_id = int(basename.split("_")[1].split(".")[0])
                with open(txt_path, "r", encoding="utf-8") as f:
                    script = f.read()
                app.pm.apply_slide_script(app.current_project, slide_id, script)
                applied += 1
            print(f"[OK] 成功应用 {applied} 页讲解稿")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
