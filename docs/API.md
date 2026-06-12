# API 参考

本文档介绍 CourseVideoGen 的核心模块和 API。

## 目录结构

```
CourseVideoGen/
├── main.py                  # 命令行入口
├── core/                    # 核心功能模块
│   ├── project_manager.py  # 项目管理
│   ├── ppt_parser.py       # PPT 解析
│   ├── html_generator.py   # HTML 渲染为图片
│   ├── llm.py              # LLM 配置与调用
│   ├── script_generator.py  # 讲解稿自动生成
│   ├── audio_generator.py  # 音频生成
│   └── video_generator.py  # 视频合成
├── models/                  # 数据模型
│   └── project.py          # Project 和 Slide 类
└── scripts/                 # 辅助脚本
```

## 核心模块

### main.py - 命令行界面

主程序入口，提供完整的命令行操作。

**命令列表：**

| 命令 | 说明 |
|------|------|
| `create <name>` | 创建新项目 |
| `load <name>` | 加载已有项目 |
| `import-ppt <file>` | 导入 PPTX 文件 |
| `import-html <file>` | 导入 HTML 幻灯片文件（Playwright 截图） |
| `script generate [--model] [--base-url] [--api-key] [--project]` | 调用 LLM 自动生成讲解稿 |
| `script apply [--project]` | 将 scripts/*.txt 回写 project.json |
| `generate-audio` | 生成音频 |
| `generate-video` | 生成视频 |
| `run-all` | 一键生成（音频+视频） |
| `list` | 列出所有项目 |

### core/project_manager.py - 项目管理

负责项目的创建、加载、保存等操作。

**主要类：ProjectManager**

```python
class ProjectManager:
    def __init__(self, base_dir: str = "workspace")
    def create_project(self, name: str) -> Project
    def load_project(self, name: str) -> Optional[Project]
    def save_project(self, project: Project)
    def add_slide(self, project: Project, image_filename: str)
    def update_slide_script(self, project: Project, slide_id: int, script: str)
    def update_slide_audio(self, project: Project, slide_id: int, audio_filename: str, duration: float)
    def list_projects(self) -> List[str]
```

### core/ppt_parser.py - PPT 解析

将 PPTX 文件解析为图片序列。

**主要类：PPTParser**

```python
class PPTParser:
    def __init__(self, project_dir: str)
    def ppt_to_images(self, pptx_path: str) -> List[str]
    def get_slide_text(self, pptx_path: str) -> List[str]
```

**渲染策略（自动选择）：**
1. Windows: pywin32 + PowerPoint COM（效果最好）
2. 跨平台: LibreOffice
3. 保底: 提取文本 + Pillow 生成占位图

### core/html_generator.py - HTML 渲染

使用 Playwright 将 HTML 幻灯片渲染为图片。

> HTML 幻灯片文件由上游 CoursePPTGen 生成，本项目只负责渲染截图。

**主要类：HTMLSlideRenderer**

```python
class HTMLSlideRenderer:
    def __init__(self, project_dir: str)
    def render_to_images(self, html_path: str) -> List[str]
```

**依赖：** 需要安装 `playwright` 并执行 `playwright install chromium`。

### core/llm.py - LLM 配置与调用

提供 LLM 调用功能，支持 OpenAI 兼容 API。

**主要函数：**

```python
@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float

def resolve_llm_config(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> LLMConfig

def extract_json(text: str) -> dict
def call_llm(system_prompt: str, user_text: str, config: LLMConfig) -> str
```

**配置优先级：** CLI 参数 > 环境变量 > 默认值

| 环境变量 | 说明 |
|---------|------|
| `OPENAI_API_KEY` | API 密钥（必填） |
| `OPENAI_BASE_URL` | API 地址（默认：https://open.bigmodel.cn/api/paas/v4） |
| `CVG_MODEL` | 模型名称（默认：glm-4-flash） |

**安装：** `pip install coursevideogen[llm]`

### core/script_generator.py - 讲解稿自动生成

调用 LLM 自动生成课程讲解稿和概览。

**主要函数：**

```python
def generate_overview(project: Project, config: LLMConfig) -> Dict
def generate_scripts(project: Project, config: LLMConfig, project_dir: str) -> List[str]
```

**工作流程：**

1. `generate_overview` - 读取所有幻灯片内容，生成结构化课程概览（写入 `project.overview`）
2. `generate_scripts` - 逐页生成口语化讲解稿，写入 `scripts/slide_XX.txt` 并回写 `slide.script`

### core/audio_generator.py - 音频生成

使用 Edge-TTS 生成讲解音频。

**主要类：AudioGenerator**

```python
class AudioGenerator:
    def __init__(self, project_dir: str)
    async def generate_audio(self, text: str, output_filename: str,
                             voice: str = "zh-CN-XiaoxiaoNeural",
                             rate: str = "+0%") -> Tuple[str, float]
    def _get_audio_duration(self, audio_path: str) -> float
    @staticmethod
    def list_voices() -> List[str]
```

**可用发音人：**

| ID | 说明 |
|----|------|
| zh-CN-XiaoxiaoNeural | 女声（默认） |
| zh-CN-YunxiNeural | 男声 |
| zh-CN-YunyangNeural | 男声 |
| zh-CN-XiaoyiNeural | 女声 |
| zh-HK-HiuMaanNeural | 粤语 |
| zh-TW-HsiaoChenNeural | 台湾腔 |

### core/video_generator.py - 视频合成

将图片和音频合成为视频。

**主要类：VideoGenerator**

```python
class VideoGenerator:
    def __init__(self, project_dir: str)
    def generate_silent_video(self, slides: List[Slide], output_path: str) -> str
    def merge_audio_video(self, slides: List[Slide], silent_video_path: str, output_path: str)
    def generate_final_video(self, slides: List[Slide], output_path: str) -> str
```

## 数据模型

### models/project.py

```python
from dataclasses import dataclass

@dataclass
class Slide:
    id: int
    image: str
    script: str = ""
    audio: Optional[str] = None
    duration: float = 3.0

@dataclass
class Project:
    name: str
    slides: List[Slide]
    created_at: str = ""
    updated_at: str = ""
```

## 工作目录结构

```
workspace/
└── <项目名>/
    ├── project.json      # 项目元数据
    ├── slides/          # 幻灯片图片（PNG）
    ├── scripts/         # 讲解稿文本
    ├── audios/          # 生成的音频（MP3）
    └── output.mp4       # 最终视频
```

## project.json 格式

```json
{
    "name": "项目名称",
    "slides": [
        {
            "id": 1,
            "image": "slide_01.png",
            "script": "讲解稿内容",
            "audio": "audio_01.mp3",
            "duration": 5.06
        }
    ],
    "created_at": "2026-04-27T...",
    "updated_at": "2026-04-27T..."
}
```

## 辅助工具

### fix_duration.py

修复已有项目的音频时长问题。

```bash
python scripts/fix_duration.py "项目名称"
```

此脚本会重新读取所有音频文件的实际时长并更新 project.json。

## 扩展开发

### 添加新的发音人

在 `core/audio_generator.py` 的 `list_voices()` 方法中添加新的发音人 ID。

### 自定义视频渲染

修改 `core/video_generator.py` 中的视频编码参数。
