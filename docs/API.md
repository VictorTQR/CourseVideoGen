# API 参考

本文档介绍 CourseVideoGen 的核心模块和 API。

## 目录结构

```
CourseVideoGen/
├── main.py                  # 命令行入口
├── core/                    # 核心功能模块
│   ├── project_manager.py  # 项目管理
│   ├── ppt_parser.py       # PPT 解析
│   ├── audio_generator.py  # 音频生成
│   ├── video_generator.py  # 视频合成
│   └── html_generator.py   # HTML 幻灯片
├── models/                  # 数据模型
│   └── project.py          # Project 和 Slide 类
└── templates/              # 自定义模板目录
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
| `import-html <file>` | 导入 HTML 幻灯片配置 |
| `generate-audio` | 生成音频 |
| `generate-video` | 生成视频 |
| `run-all` | 一键生成（音频+视频） |
| `list` | 列出所有项目 |
| `list-templates` | 列出可用模板 |

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

### core/html_generator.py - HTML 幻灯片

生成和渲染 HTML 幻灯片。

**主要类：**
- `HTMLSlideGenerator`: 从 JSON 生成 HTML
- `HTMLSlideRenderer`: 将 HTML 渲染为图片

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
    ├── html/            # HTML 源文件（如果使用 HTML 模式）
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
python fix_duration.py "项目名称"
```

此脚本会重新读取所有音频文件的实际时长并更新 project.json。

## 扩展开发

### 添加新的发音人

在 `core/audio_generator.py` 的 `list_voices()` 方法中添加新的发音人 ID。

### 添加新的模板

在 `templates/` 目录下创建三个文件：
- `templatename.html` - 主模板
- `_templatename_slide.html` - 单页模板
- `templatename.json` - 颜色配置

### 自定义视频渲染

修改 `core/video_generator.py` 中的视频编码参数。
