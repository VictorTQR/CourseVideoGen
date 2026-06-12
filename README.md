# CourseVideoGen

PPT/HTML 讲解视频自动生成工具 — 将幻灯片图片和讲解稿一键合成为带语音的课程视频。

## 功能特性

- ✅ PPTX 解析为图片（pywin32 / LibreOffice / 保底文本）
- ✅ HTML 幻灯片渲染为图片（Playwright）
- ✅ 讲解稿管理
- ✅ Edge-TTS 语音生成
- ✅ 图片+音频合成视频
- ✅ 项目管理（支持多项目）
- ✅ 自动获取并使用音频实际时长

> **上游工具：** HTML 幻灯片的生成（JSON → HTML）由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责，本项目只负责渲染截图、语音合成和视频输出。

## 快速开始

### 1. 安装依赖

```bash
cd CourseVideoGen
pip install -r requirements.txt
```

### 2. 使用流程

#### 方式一：导入 PPTX

```bash
# 创建项目
python main.py create "我的第一节课"

# 导入 PPTX（需要先 create）
python main.py create "我的第一节课"
python main.py import-ppt "lesson.pptx"

# (可选) 编辑讲解稿
# 编辑 workspace/我的第一节课/scripts/slide_01.txt 等

# 生成音频和视频
python main.py run-all
```

#### 方式二：导入 HTML 幻灯片

```bash
# 1. 用 CoursePPTGen 生成 HTML 幻灯片文件

# 2. 创建项目并导入 HTML
python main.py create "HTML 演示"
python main.py import-html "slides.html"

# 3. (可选) 编辑讲解稿
# 编辑 workspace/HTML演示/scripts/slide_01.txt 等

# 4. 生成音频和视频
python main.py run-all
```

## 项目结构

```
CourseVideoGen/
├── main.py                  # 命令行入口
├── requirements.txt         # 依赖列表
├── pyproject.toml            # 项目配置（uv）
├── core/                    # 核心模块
│   ├── project_manager.py   # 项目管理
│   ├── ppt_parser.py        # PPTX → 图片
│   ├── html_generator.py    # HTML → 图片（Playwright 截图）
│   ├── audio_generator.py   # Edge-TTS 音频生成
│   └── video_generator.py    # 图片+音频 → MP4
├── models/                  # 数据模型
│   └── project.py           # Project / Slide
├── scripts/                 # 辅助脚本
│   ├── fix_duration.py      # 修复音频时长
│   └── image_to_video.py    # (旧版) 简单图片转视频
├── docs/                    # 项目文档
│   ├── PRD.md               # 产品需求文档
│   ├── API.md               # API 参考
│   ├── INSTALL.md           # 安装指南
│   ├── CHANGELOG.md         # 变更日志
│   └── index.md             # 文档目录
├── tests/                   # 测试
└── workspace/               # 项目数据目录
    └── <项目名>/
        ├── project.json     # 项目元数据
        ├── slides/          # 幻灯片图片 (PNG)
        ├── scripts/         # 讲解稿 (TXT)
        ├── audios/          # 音频文件 (MP3)
        └── output.mp4       # 最终视频
```

## 命令行参数

### 全局命令

| 命令 | 说明 |
|-----|-----|
| `list` | 列出所有项目 |
| `create <name>` | 创建新项目 |
| `load <name>` | 加载项目 |

### 项目操作

| 命令 | 说明 |
|-----|-----|
| `import-ppt <file>` | 导入 PPTX 文件（渲染为图片） |
| `import-html <file>` | 导入 HTML 幻灯片文件（Playwright 截图为图片） |
| `generate-audio` | 为每页讲解稿生成语音 |
| `generate-video` | 将图片+音频合成视频 |
| `run-all` | 一键生成音频和视频 |

### 通用选项

| 选项 | 说明 | 适用命令 |
|-----|-----|-----|
| `--project <名>` | 指定项目 | generate-audio / generate-video / run-all |
| `--voice <发音人>` | 指定 TTS 发音人 | generate-audio / run-all |
| `--output <文件>` | 输出视频文件名 | generate-video / run-all |

## 可用发音人

| 发音人 ID | 说明 |
|----------|-----|
| `zh-CN-XiaoxiaoNeural` | 女声（默认） |
| `zh-CN-YunxiNeural` | 男声 |
| `zh-CN-YunyangNeural` | 男声 |
| `zh-CN-XiaoyiNeural` | 女声 |
| `zh-HK-HiuMaanNeural` | 粤语 |
| `zh-TW-HsiaoChenNeural` | 台湾腔 |

示例：
```bash
python main.py generate-audio --voice zh-CN-YunxiNeural
```

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| PPTX 解析 | python-pptx | 提取文本和布局 |
| PPT 渲染 | pywin32 (Win) / LibreOffice (Linux/Mac) | PPTX → 图片 |
| HTML 渲染 | Playwright | HTML → 图片截图 |
| TTS | edge-tts | 微软语音合成 |
| 视频合成 | moviepy 1.x | 图片+音频 → MP4 |
| 音频元数据 | mutagen | 读取 MP3 时长 |

## 常见问题

### Q: PPT 转图片不清晰？

A: 不同平台有不同的最优方案：

**Windows (推荐):**
```bash
pip install pywin32
```
使用 pywin32 调用本机 PowerPoint，渲染效果最好。

**Linux/macOS:**
```bash
# Ubuntu/Debian
apt update && apt install -y libreoffice

# macOS
brew install libreoffice
```

如果都没有安装，会使用保底模式：提取 PPT 文本，生成简单的占位图。

### Q: import-html 报错找不到 Playwright？

A: 安装 Playwright 及浏览器：
```bash
pip install playwright
playwright install chromium
```

### Q: 如何调整语速？

A: 修改 `core/audio_generator.py` 中的 `rate` 参数，例如 `rate="+10%"` 或 `rate="-10%"`。

### Q: 每一页的显示时长如何确定？

A: 等于该页讲解音频的实际时长，使用 `mutagen` 库自动读取 MP3 文件时长。

### Q: 发现时长不对怎么办？

A: 运行修复脚本：
```bash
python scripts/fix_duration.py "项目名称"
```

### Q: 支持哪些视频格式？

A: 默认输出 `.mp4` (H.264 + AAC)，兼容性最好。

## 与 CoursePPTGen 的配合

CourseVideoGen 是下游工具，负责把幻灯片变成带语音的视频。幻灯片本身由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 生成：

```
CoursePPTGen (JSON → HTML/PPTX)
    │
    ├── PPTX ──→ CourseVideoGen import-ppt ──→ 图片
    └── HTML  ──→ CourseVideoGen import-html ─→ 图片
                      │
                      ▼
              讲解稿 + Edge-TTS → 音频
                      │
                      ▼
              图片 + 音频 → MP4 视频
```

## 后续计划

- [ ] Web UI (Gradio/Streamlit)
- [ ] 自动生成字幕 (.srt)
- [ ] 视频转场效果
- [ ] 音频预览功能
- [ ] 支持 Markdown 导入

## License

MIT
