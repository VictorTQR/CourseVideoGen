# CourseVideoGen

PPT/HTML 讲解视频自动生成工具 — 将幻灯片图片和讲解稿一键合成为带语音的课程视频。

## 功能特性

- ✅ PPTX 解析为图片（pywin32 / LibreOffice / 保底文本）
- ✅ HTML 幻灯片渲染为图片（Playwright）
- ✅ LLM 自动生成口语化讲解稿（两阶段：课程概览 → 逐页讲稿）
- ✅ Edge-TTS 语音生成
- ✅ 图片+音频合成视频
- ✅ 项目管理（支持多项目）
- ✅ 自动获取并使用音频实际时长

> **上游工具：** HTML 幻灯片的生成（JSON → HTML）由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责，本项目只负责渲染截图、讲解稿生成、语音合成和视频输出。

## 快速开始

### 1. 安装依赖

```bash
cd CourseVideoGen
pip install -r requirements.txt
# 或
uv sync
```

### 2. 完整工作流

```bash
# 1. 创建项目
cvg create "我的第一节课"

# 2. 导入幻灯片（PPTX 或 HTML）
cvg import-ppt "lesson.pptx" -p "我的第一节课"
# 或
cvg import-html "slides.html" -p "我的第一节课"

# 3. 自动生成讲解稿（需要 LLM API）
#    也可通过环境变量 OPENAI_API_KEY / OPENAI_BASE_URL 设置
cvg script generate -p "我的第一节课" --api-key "your-key"

# 4. 生成音频和视频
cvg run-all -p "我的第一节课"
```

> `script generate` 生成后自动回写 project.json，大多数情况直接跑下一步即可。
> 如需修改讲解稿，编辑 `scripts/*.txt` 后执行 `script apply`。

### 3. 流程总览

```
create          → project.json (空壳)
import          → slides/*.png, project.json { id, image, content }
script generate → scripts/*.txt + 自动回写 project.json { script, overview }
script apply    → project.json { script } (可选，仅在编辑 txt 后执行)
generate-audio  → audios/*.mp3, project.json { audio, duration }
generate-video  → output.mp4
```

## 项目结构

```
CourseVideoGen/
├── main.py                  # CLI 入口（Typer）
├── pyproject.toml           # 项目配置（uv）
├── requirements.txt         # 依赖列表
├── core/                    # 核心模块
│   ├── project_manager.py   # 项目管理
│   ├── ppt_parser.py        # PPTX → 图片
│   ├── html_generator.py    # HTML → 图片（Playwright 截图）
│   ├── script_generator.py  # LLM 讲解稿生成（overview + 逐页 script）
│   ├── llm.py               # LLM 配置解析 / 调用 / JSON 提取
│   ├── audio_generator.py   # Edge-TTS 音频生成
│   └── video_generator.py   # 图片+音频 → MP4
├── models/                  # 数据模型
│   └── project.py           # Project / Slide
├── scripts/                 # 辅助脚本
│   ├── fix_duration.py      # 修复音频时长
│   └── image_to_video.py    # (旧版) 简单图片转视频
├── tests/                   # 测试
├── docs/                    # 项目文档
│   ├── PRD.md               # 产品需求文档
│   ├── REFACTOR_SPEC.md     # 重构说明
│   ├── API.md               # API 参考
│   ├── INSTALL.md           # 安装指南
│   ├── CHANGELOG.md         # 变更日志
│   └── index.md             # 文档目录
└── workspace/               # 项目数据目录
    └── <项目名>/
        ├── project.json     # 项目元数据（唯一权威数据源）
        ├── slides/          # 幻灯片图片 (PNG)
        ├── scripts/         # 讲解稿 (TXT，用户可编辑)
        ├── audios/          # 音频文件 (MP3)
        └── output.mp4       # 最终视频
```

## 命令行参数

### 项目管理

| 命令 | 说明 |
|-----|-----|
| `create <name>` | 创建新项目 |
| `list` | 列出所有项目 |

### 导入

| 命令 | 说明 |
|-----|-----|
| `import-ppt <file> -p <项目>` | 导入 PPTX 文件，渲染为图片并提取文本 |
| `import-html <file> -p <项目>` | 导入 HTML 幻灯片文件，Playwright 截图并提取文本 |

### 讲解稿

| 命令 | 说明 |
|-----|-----|
| `script generate -p <项目>` | LLM 自动生成讲解稿，自动回写 project.json |
| `script apply -p <项目>` | 将编辑后的 scripts/*.txt 回写到 project.json |

### 音视频

| 命令 | 说明 |
|-----|-----|
| `generate-audio -p <项目>` | 为每页讲解稿生成语音 |
| `generate-video -p <项目>` | 将图片+音频合成为视频 |
| `run-all -p <项目>` | 一键生成音频和视频 |

### 通用选项

| 选项 | 短选项 | 说明 |
|-----|-----|-----|
| `--project <名>` | `-p` | 指定项目（所有需项目的命令必传） |
| `--output <文件>` | `-o` | 输出视频文件名（默认 output.mp4） |
| `--voice <发音人>` | | TTS 发音人（默认 zh-CN-XiaoxiaoNeural） |
| `--rate <语速>` | | TTS 语速（默认 +0%） |
| `--model <模型>` | | LLM 模型（默认 glm-4-flash） |
| `--base-url <地址>` | | LLM API 地址 |
| `--api-key <密钥>` | | LLM API 密钥 |

LLM 配置优先级：`CLI 参数 > 环境变量 > 默认值`

环境变量：
- `OPENAI_API_KEY` — API 密钥
- `OPENAI_BASE_URL` — API 地址（默认 `https://open.bigmodel.cn/api/paas/v4`）
- `CVG_MODEL` — 模型名（默认 `glm-4-flash`）

## 可用发音人

| 发音人 ID | 说明 |
|----------|-----|
| `zh-CN-XiaoxiaoNeural` | 女声（默认） |
| `zh-CN-YunxiNeural` | 男声 |
| `zh-CN-YunyangNeural` | 男声 |
| `zh-CN-XiaoyiNeural` | 女声 |
| `zh-HK-HiuMaanNeural` | 粤语 |
| `zh-TW-HsiaoChenNeural` | 台湾腔 |

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| CLI | Typer + loguru | 命令行框架 + 日志 |
| PPTX 解析 | python-pptx | 提取文本和布局 |
| PPT 渲染 | pywin32 (Win) / LibreOffice (Linux/Mac) | PPTX → 图片 |
| HTML 渲染 | Playwright | HTML → 图片截图 |
| 讲解稿生成 | OpenAI API 兼容 | LLM 生成口语化讲稿 |
| TTS | edge-tts | 微软语音合成 |
| 视频合成 | moviepy 1.x | 图片+音频 → MP4 |
| 音频元数据 | mutagen | 读取 MP3 时长 |

## 常见问题

### Q: PPT 转图片不清晰？

**Windows (推荐):**
```bash
pip install pywin32
```

**Linux/macOS:**
```bash
# Ubuntu/Debian
apt update && apt install -y libreoffice
# macOS
brew install libreoffice
```

### Q: import-html 报错找不到 Playwright？

```bash
pip install playwright
playwright install chromium
```

### Q: script generate 报错缺少 API Key？

设置环境变量或在命令中传入：
```bash
# 环境变量
export OPENAI_API_KEY="your-key"

# 或命令行
cvg script generate -p "课" --api-key "your-key"
```

### Q: 如何调整语速？

使用 `--rate` 参数：
```bash
cvg generate-audio -p "课" --rate "+10%"
```

### Q: 每一页的显示时长如何确定？

等于该页讲解音频的实际时长，使用 `mutagen` 库自动读取 MP3 文件时长。

### Q: 发现时长不对怎么办？

```bash
python scripts/fix_duration.py "项目名称"
```

### Q: 支持哪些视频格式？

默认输出 `.mp4` (H.264 + AAC)，兼容性最好。

## 与 CoursePPTGen 的配合

```
CoursePPTGen (JSON → HTML/PPTX)
    │
    ├── PPTX ──→ CourseVideoGen import-ppt ──→ 图片 + content
    └── HTML  ──→ CourseVideoGen import-html ─→ 图片 + content
                      │
                      ▼
              script generate → LLM 讲解稿 → scripts/*.txt + project.json
                      │
                      ▼
              generate-audio → Edge-TTS → audios/*.mp3
                      │
                      ▼
              generate-video → moviepy → output.mp4
```

## 后续计划

- [ ] Web UI (Gradio/Streamlit)
- [ ] 自动生成字幕 (.srt)
- [ ] 视频转场效果
- [ ] 音频预览功能
- [ ] 支持 Markdown 导入

## License

MIT
