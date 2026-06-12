# API 参考

本文档介绍 CourseVideoGen 的核心模块和 API。

## 目录结构

```
CourseVideoGen/
├── main.py                  # CLI 入口（Typer）
├── core/                    # 核心功能模块
│   ├── project_manager.py  # 项目管理
│   ├── ppt_parser.py       # PPT 解析
│   ├── html_generator.py   # HTML 渲染为图片
│   ├── script_generator.py # LLM 讲解稿生成
│   ├── llm.py              # LLM 配置 / 调用 / JSON 提取
│   ├── audio_generator.py  # 音频生成
│   └── video_generator.py  # 视频合成
├── models/                  # 数据模型
│   └── project.py          # Project 和 Slide 类
└── scripts/                 # 辅助脚本
```

## CLI 命令

| 命令 | 说明 |
|------|------|
| `create <name>` | 创建新项目 |
| `list` | 列出所有项目 |
| `import-ppt <file> -p <项目>` | 导入 PPTX |
| `import-html <file> -p <项目>` | 导入 HTML 幻灯片 |
| `script generate -p <项目>` | LLM 生成讲解稿 |
| `script apply -p <项目>` | 回写编辑后的讲解稿 |
| `generate-audio -p <项目>` | 生成音频 |
| `generate-video -p <项目>` | 生成视频 |
| `run-all -p <项目>` | 一键生成音频和视频 |

所有需项目的命令通过 `-p` / `--project` 指定，无进程内状态。

## 核心模块

### core/llm.py - LLM 基础层

配置解析、LLM 调用、响应 JSON 提取。

```python
@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float

def resolve_llm_config(api_key=None, base_url=None, model=None, temperature=None) -> LLMConfig
def extract_json(text: str) -> dict
def call_llm(system_prompt: str, user_text: str, config: LLMConfig) -> str
```

配置优先级：`CLI 参数 > 环境变量 > 默认值`

环境变量：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`CVG_MODEL`

### core/project_manager.py - 项目管理

```python
class ProjectManager:
    def create_project(name: str) -> Project
    def load_project(name: str) -> Optional[Project]
    def add_slide(project: Project, image_filename: str) -> Slide
    def update_slide_content(project: Project, slide_id: int, content: str)
    def apply_slide_script(project: Project, slide_id: int, script: str)
    def update_overview(project: Project, overview: dict)
    def update_slide_audio(project: Project, slide_id: int, audio_filename: str, duration: float)
    def list_projects() -> list
```

### core/ppt_parser.py - PPT 解析

```python
class PPTParser:
    def ppt_to_images(pptx_path: str) -> List[str]
    def get_slide_text(pptx_path: str) -> List[str]
```

渲染策略（自动选择）：
1. Windows: pywin32 + PowerPoint COM
2. 跨平台: LibreOffice
3. 保底: 提取文本 + Pillow 生成占位图

### core/html_generator.py - HTML 渲染

```python
class HTMLSlideRenderer:
    def render_to_images(html_path: str) -> List[Tuple[str, str]]
    # 返回 [(image_filename, text_content), ...]
```

依赖：`playwright` + `playwright install chromium`

### core/script_generator.py - 讲解稿生成

两阶段 LLM 生成：

```python
def generate_overview(project: Project, config: LLMConfig) -> Dict
    # Phase 1: 读取所有 slide.content，生成课程概览
    # 返回 overview dict，由调用方持久化

def generate_scripts(project: Project, config: LLMConfig, project_dir: str) -> Dict[int, str]
    # Phase 2: 逐页生成讲解稿
    # 写入 scripts/*.txt，返回 {slide_id: script_text}
    # 单页失败重试 2 次后跳过
```

### core/audio_generator.py - 音频生成

```python
class AudioGenerator:
    async def generate_audio(text, output_filename, voice, rate) -> Tuple[str, float]
    def _get_audio_duration(audio_path: str) -> float
    @staticmethod
    def list_voices() -> list
```

### core/video_generator.py - 视频合成

```python
class VideoGenerator:
    def generate_silent_video(slides, output_path) -> str
    def merge_audio_video(slides, silent_video_path, output_path)
    def generate_final_video(slides, output_path) -> str
```

## 数据模型

### models/project.py

```python
@dataclass
class Slide:
    id: int
    image: str                     # 图片文件名
    content: str = ""              # PPT/HTML 原始内容
    script: Optional[str] = None   # LLM 生成的讲解稿
    audio: Optional[str] = None    # 音频文件名
    duration: Optional[float] = None  # 显示时长（秒）

@dataclass
class Project:
    name: str
    slides: List[Slide]
    created_at: str = ""
    updated_at: str = ""
    overview: Optional[Dict] = None  # 课程概览（script generate 阶段）
```

`from_dict` 兼容旧格式：缺少 `content` 时从 `script` 迁移。

## project.json 示例

```json
{
    "name": "Python入门课",
    "overview": {
        "course_summary": "Python 编程入门课程",
        "target_audience": "零基础学员",
        "tone": "轻松活泼",
        "slide_overview": [
            {"id": 1, "topic": "课程介绍", "key_points": ["什么是Python", "为什么学Python"]}
        ]
    },
    "slides": [
        {
            "id": 1,
            "image": "slide_01.png",
            "content": "Python简介\n- 通用编程语言\n- 简单易学",
            "script": "大家好，今天我们来学习 Python 编程语言...",
            "audio": "audio_01.mp3",
            "duration": 12.5
        }
    ],
    "created_at": "2026-05-30T10:00:00",
    "updated_at": "2026-05-30T11:00:00"
}
```

## 辅助工具

### fix_duration.py

```bash
python scripts/fix_duration.py "项目名称"
```

## 扩展开发

### 添加新的发音人

在 `core/audio_generator.py` 的 `list_voices()` 方法中添加。

### 自定义视频渲染

修改 `core/video_generator.py` 中的视频编码参数。
