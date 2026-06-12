"""
HTML 幻灯片渲染模块 - 使用 Playwright 将 HTML 转为图片

注意：HTML 生成由 CoursePPTGen 项目负责，本项目只负责渲染截图。
"""
import os
from typing import List


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
