"""
HTML 幻灯片生成和渲染模块
支持从 JSON/Markdown 生成 HTML 幻灯片，并用 Playwright 渲染为图片
支持自定义模板系统
"""
import os
import json
from typing import List, Dict, Optional


# 内置模板系统
BUILTIN_TEMPLATES = {
    "default": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: {bg_color};
        }
        .slide {
            width: 1920px;
            height: 1080px;
            padding: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: {bg_color};
        }
        .slide-title {
            font-size: 72px;
            font-weight: bold;
            color: {text_color};
            margin-bottom: 60px;
            line-height: 1.2;
        }
        .slide-subtitle {
            font-size: 42px;
            color: {text_color};
            opacity: 0.8;
            margin-bottom: 40px;
        }
        .slide-content {
            font-size: 36px;
            color: {text_color};
            line-height: 1.8;
        }
        .slide-content ul {
            padding-left: 60px;
        }
        .slide-content li {
            margin-bottom: 20px;
        }
        .slide-page-number {
            position: absolute;
            bottom: 40px;
            right: 60px;
            font-size: 24px;
            color: {text_color};
            opacity: 0.5;
        }
    </style>
</head>
<body>
    {slides_html}
</body>
</html>
""",
    "minimal": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: {bg_color};
        }
        .slide {
            width: 1920px;
            height: 1080px;
            padding: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: {bg_color};
            position: relative;
        }
        .slide-title {
            font-size: 64px;
            font-weight: 600;
            color: {text_color};
            margin-bottom: 48px;
            line-height: 1.3;
            letter-spacing: -0.5px;
        }
        .slide-subtitle {
            font-size: 32px;
            color: {text_color};
            opacity: 0.6;
            margin-bottom: 56px;
            font-weight: 400;
        }
        .slide-content {
            font-size: 28px;
            color: {text_color};
            line-height: 1.9;
            font-weight: 400;
        }
        .slide-content ul {
            padding-left: 0;
            list-style: none;
        }
        .slide-content li {
            margin-bottom: 24px;
            padding-left: 32px;
            position: relative;
        }
        .slide-content li::before {
            content: "";
            position: absolute;
            left: 0;
            top: 16px;
            width: 8px;
            height: 8px;
            background: {accent_color};
            border-radius: 50%;
        }
        .slide-footer {
            position: absolute;
            bottom: 48px;
            left: 120px;
            right: 120px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 20px;
            color: {text_color};
            opacity: 0.4;
        }
        .slide-divider {
            width: 80px;
            height: 4px;
            background: {accent_color};
            margin-bottom: 48px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    {slides_html}
</body>
</html>
""",
    "dark": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        .slide {
            width: 1920px;
            height: 1080px;
            padding: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: transparent;
        }
        .slide-title {
            font-size: 72px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 60px;
            line-height: 1.2;
            text-shadow: 0 2px 20px rgba(0,0,0,0.3);
        }
        .slide-subtitle {
            font-size: 42px;
            color: #a0a0ff;
            margin-bottom: 40px;
        }
        .slide-content {
            font-size: 36px;
            color: #e0e0e0;
            line-height: 1.8;
        }
        .slide-content ul {
            padding-left: 60px;
        }
        .slide-content li {
            margin-bottom: 20px;
        }
        .slide-page-number {
            position: absolute;
            bottom: 40px;
            right: 60px;
            font-size: 24px;
            color: #8080a0;
        }
        .slide-decoration {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
    </style>
</head>
<body>
    {slides_html}
</body>
</html>
""",
    "code": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "Fira Code", "JetBrains Mono", "Consolas", "Microsoft YaHei", monospace;
            background: #282c34;
        }
        .slide {
            width: 1920px;
            height: 1080px;
            padding: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #282c34;
            position: relative;
        }
        .slide::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 8px;
            background: linear-gradient(90deg, #61afef, #98c379, #e5c07b, #e06c75);
        }
        .slide-title {
            font-size: 64px;
            font-weight: 700;
            color: #61afef;
            margin-bottom: 48px;
            line-height: 1.2;
        }
        .slide-subtitle {
            font-size: 36px;
            color: #98c379;
            margin-bottom: 40px;
            font-weight: 500;
        }
        .slide-content {
            font-size: 32px;
            color: #abb2bf;
            line-height: 1.8;
        }
        .slide-content ul {
            padding-left: 40px;
        }
        .slide-content li {
            margin-bottom: 20px;
        }
        .slide-content code {
            background: #21252b;
            padding: 4px 12px;
            border-radius: 6px;
            color: #e5c07b;
        }
        .slide-page-number {
            position: absolute;
            bottom: 40px;
            right: 60px;
            font-size: 24px;
            color: #5c6370;
        }
    </style>
</head>
<body>
    {slides_html}
</body>
</html>
"""
}

# 内置单页模板
SLIDE_TEMPLATES = {
    "default": """
<div class="slide" id="slide-{index}" style="position: relative;">
    {content}
    <div class="slide-page-number">{index} / {total}</div>
</div>
""",
    "minimal": """
<div class="slide" id="slide-{index}" style="position: relative;">
    {content}
    <div class="slide-footer">
        <span>{title}</span>
        <span>{index} / {total}</span>
    </div>
</div>
""",
    "dark": """
<div class="slide" id="slide-{index}" style="position: relative;">
    <div class="slide-decoration"></div>
    {content}
    <div class="slide-page-number">{index} / {total}</div>
</div>
""",
    "code": """
<div class="slide" id="slide-{index}" style="position: relative;">
    {content}
    <div class="slide-page-number">{index} / {total}</div>
</div>
"""
}

# 模板配置
TEMPLATE_CONFIGS = {
    "default": {
        "light": {"bg_color": "#ffffff", "text_color": "#1a1a2e", "accent_color": "#667eea"},
        "dark": {"bg_color": "#1a1a2e", "text_color": "#ffffff", "accent_color": "#667eea"}
    },
    "minimal": {
        "light": {"bg_color": "#fafafa", "text_color": "#1a1a1a", "accent_color": "#007aff"},
        "dark": {"bg_color": "#1c1c1e", "text_color": "#f2f2f7", "accent_color": "#0a84ff"}
    },
    "dark": {
        "light": {"bg_color": "#1a1a2e", "text_color": "#ffffff", "accent_color": "#667eea"},
        "dark": {"bg_color": "#1a1a2e", "text_color": "#ffffff", "accent_color": "#667eea"}
    },
    "code": {
        "light": {"bg_color": "#282c34", "text_color": "#abb2bf", "accent_color": "#61afef"},
        "dark": {"bg_color": "#282c34", "text_color": "#abb2bf", "accent_color": "#61afef"}
    }
}


class HTMLSlideGenerator:
    """HTML 幻灯片生成器 - 支持自定义模板"""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.html_dir = os.path.join(project_dir, "html")
        self.slides_dir = os.path.join(project_dir, "slides")
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        os.makedirs(self.html_dir, exist_ok=True)

    def list_available_templates(self) -> List[str]:
        """列出所有可用的模板"""
        templates = list(BUILTIN_TEMPLATES.keys())
        
        # 检查自定义模板
        if os.path.exists(self.templates_dir):
            # 优先检查子目录结构（新结构）
            for filename in os.listdir(self.templates_dir):
                dir_path = os.path.join(self.templates_dir, filename)
                if os.path.isdir(dir_path):
                    if os.path.exists(os.path.join(dir_path, "template.html")):
                        if filename not in templates:
                            templates.append(filename)
                    continue
            
            # 向后兼容：检查旧的文件结构
            for filename in os.listdir(self.templates_dir):
                if filename.endswith(".html") and not filename.startswith("_"):
                    template_name = filename[:-5]  # 去掉 .html
                    if template_name not in templates:
                        templates.append(template_name)
        
        return templates

    def _load_template(self, template_name: str) -> tuple[str, str, dict]:
        """
        加载模板
        
        Returns:
            (html_template, slide_template, config)
        """
        # 先检查是否是内置模板
        if template_name in BUILTIN_TEMPLATES:
            return (
                BUILTIN_TEMPLATES[template_name],
                SLIDE_TEMPLATES.get(template_name, SLIDE_TEMPLATES["default"]),
                TEMPLATE_CONFIGS.get(template_name, TEMPLATE_CONFIGS["default"])
            )
        
        # 优先尝试新的目录结构
        template_dir = os.path.join(self.templates_dir, template_name)
        if os.path.isdir(template_dir):
            template_path = os.path.join(template_dir, "template.html")
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    html_template = f.read()
                
                # 加载单页模板
                slide_template = SLIDE_TEMPLATES["default"]
                slide_path = os.path.join(template_dir, "slide.html")
                if os.path.exists(slide_path):
                    with open(slide_path, "r", encoding="utf-8") as f:
                        slide_template = f.read()
                
                # 加载配置
                config = TEMPLATE_CONFIGS["default"]
                config_path = os.path.join(template_dir, "config.json")
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                
                return html_template, slide_template, config
        
        # 向后兼容：检查旧的文件结构
        custom_template_path = os.path.join(self.templates_dir, f"{template_name}.html")
        if os.path.exists(custom_template_path):
            with open(custom_template_path, "r", encoding="utf-8") as f:
                html_template = f.read()
            
            # 加载单页模板
            slide_template = SLIDE_TEMPLATES["default"]
            custom_slide_template_path = os.path.join(self.templates_dir, f"_{template_name}_slide.html")
            if os.path.exists(custom_slide_template_path):
                with open(custom_slide_template_path, "r", encoding="utf-8") as f:
                    slide_template = f.read()
            
            # 加载配置
            config = TEMPLATE_CONFIGS["default"]
            custom_config_path = os.path.join(self.templates_dir, f"{template_name}.json")
            if os.path.exists(custom_config_path):
                with open(custom_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            return html_template, slide_template, config
        
        # 模板不存在，回退到默认
        print(f"⚠️  模板 '{template_name}' 不存在，使用默认模板")
        return (
            BUILTIN_TEMPLATES["default"],
            SLIDE_TEMPLATES["default"],
            TEMPLATE_CONFIGS["default"]
        )

    def generate_from_json(self, json_path: str, template_name: str = "default") -> str:
        """
        从 JSON 配置生成 HTML 幻灯片
        
        JSON 格式示例:
        {
            "title": "我的课程",
            "theme": "dark",
            "template": "minimal",  // 可选
            "slides": [...]
        }
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # JSON 中也可以指定模板
        if "template" in data and template_name == "default":
            template_name = data["template"]
        
        return self._generate_html(data, template_name)

    def generate_simple(self, slides_data: List[Dict], title: str = "幻灯片",
                       theme: str = "light", template_name: str = "default") -> str:
        """直接从数据生成 HTML"""
        data = {
            "title": title,
            "theme": theme,
            "slides": slides_data
        }
        return self._generate_html(data, template_name)

    def _copy_template_resources(self, template_name: str):
        """复制模板目录下的资源文件到 HTML 目录"""
        # 先尝试新的目录结构
        template_dir = os.path.join(self.templates_dir, template_name)
        if os.path.isdir(template_dir):
            for filename in os.listdir(template_dir):
                # 跳过模板文件本身，只复制资源文件
                if filename in ["template.html", "slide.html", "config.json"]:
                    continue
                src_path = os.path.join(template_dir, filename)
                if os.path.isfile(src_path):
                    dst_path = os.path.join(self.html_dir, filename)
                    import shutil
                    shutil.copy2(src_path, dst_path)
                    print(f"📦 复制资源文件: {filename}")

    def _generate_html(self, data: Dict, template_name: str = "default") -> str:
        """内部 HTML 生成逻辑 - 支持自定义模板"""
        # 加载模板
        html_template, slide_template, template_config = self._load_template(template_name)
        
        theme = data.get("theme", "light")
        if theme not in template_config:
            theme = "light"
        
        colors = template_config[theme]
        
        # 生成幻灯片内容
        slides_html = ""
        slides = data.get("slides", [])
        total = len(slides)
        project_title = data.get("title", "幻灯片")

        for i, slide in enumerate(slides, 1):
            content_parts = []

            if slide.get("title"):
                content_parts.append(f'<div class="slide-title">{slide["title"]}</div>')
            if slide.get("subtitle"):
                content_parts.append(f'<div class="slide-subtitle">{slide["subtitle"]}</div>')
            
            # 一些模板支持分隔线
            if template_name == "minimal" and content_parts:
                content_parts.append('<div class="slide-divider"></div>')
            
            if slide.get("content"):
                slide_content = slide["content"]
                # 简单处理列表
                if isinstance(slide_content, list):
                    items = "".join(f"<li>{item}</li>" for item in slide_content)
                    slide_content = f"<ul>{items}</ul>"
                content_parts.append(f'<div class="slide-content">{slide_content}</div>')

            # 使用当前模板的单页模板
            slide_html = slide_template.format(
                index=i,
                total=total,
                title=project_title,
                content="\n".join(content_parts)
            )
            slides_html += slide_html

        # 使用当前模板的 HTML 框架
        html_content = html_template.format(
            title=project_title,
            bg_color=colors.get("bg_color", "#ffffff"),
            text_color=colors.get("text_color", "#1a1a2e"),
            accent_color=colors.get("accent_color", "#667eea"),
            slides_html=slides_html
        )

        output_path = os.path.join(self.html_dir, "slides.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # 复制模板资源文件
        self._copy_template_resources(template_name)

        print(f"✅ HTML 幻灯片已生成 (模板: {template_name}): {output_path}")
        return output_path


class HTMLSlideRenderer:
    """HTML 幻灯片渲染器 - 使用 Playwright 将 HTML 转为图片"""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.html_dir = os.path.join(project_dir, "html")
        self.slides_dir = os.path.join(project_dir, "slides")

    def render_to_images(self, html_path: str) -> List[str]:
        """
        将 HTML 幻灯片渲染为图片序列
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ Playwright 未安装")
            print("   请运行: pip install playwright && playwright install chromium")
            return []

        print("🔄 使用 Playwright 渲染 HTML 幻灯片...")

        images = []
        html_file = f"file://{os.path.abspath(html_path)}"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                page.goto(html_file, wait_until="networkidle")

                # 获取幻灯片数量
                slide_count = page.evaluate("() => document.querySelectorAll('.slide').length")

                for i in range(1, slide_count + 1):
                    # 显示当前幻灯片
                    page.evaluate(f"""() => {{
                        const slides = document.querySelectorAll('.slide');
                        slides.forEach((s, idx) => {{
                            s.style.display = (idx === {i-1}) ? 'flex' : 'none';
                        }});
                    }}""")

                    # 截图
                    filename = f"slide_{i:02d}.png"
                    filepath = os.path.join(self.slides_dir, filename)

                    # 只截取幻灯片区域
                    slide_elem = page.query_selector(f"#slide-{i}")
                    if slide_elem:
                        slide_elem.screenshot(path=filepath)
                    else:
                        page.screenshot(path=filepath)

                    images.append(filename)
                    print(f"   第 {i}/{slide_count} 页: {filename}")

                browser.close()

            print(f"✅ HTML 渲染完成: {len(images)} 页")
            return images

        except Exception as e:
            print(f"❌ Playwright 渲染失败: {e}")
            return []
