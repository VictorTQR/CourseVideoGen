# CourseVideoGen

PPT 讲解视频自动生成工具 - 只需提供 PPTX 和讲解稿，一键生成带音频的课程视频。

## 更新日志

### 2026-04-27
- **修复**: 修复音频时长获取问题，使用 mutagen 库替代 moviepy 读取时长
- **新增**: 添加 fix_duration.py 脚本，支持修复已有项目的音频时长
- **改进**: 固定 moviepy 版本 < 2.0（2.x API 不兼容）
- **改进**: video_generator.py 添加安全检查，确保使用正确音频时长

## 功能特性

- ✅ PPTX 解析为图片
- ✅ HTML 幻灯片（无需 PPT，用 JSON 配置）
- ✅ 讲解稿管理
- ✅ Edge-TTS 语音生成
- ✅ 图片+音频合成视频
- ✅ 项目管理（支持多项目）
- ✅ 自动获取并使用音频实际时长
- ✅ 支持修复已有项目的音频时长

## 快速开始

### 1. 安装依赖

```bash
cd CourseVideoGen
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 完整使用流程

#### 方式一：使用 PPTX
```bash
# 创建项目
python main.py create "我的第一节课"

# 导入 PPTX
python main.py import-ppt "lesson.pptx" --project "我的第一节课"

# (可选) 编辑讲解稿
# 编辑 workspace/我的第一节课/scripts/slide_01.txt 等

# 生成音频
python main.py generate-audio --project "我的第一节课"

# 生成视频
python main.py generate-video --project "我的第一节课"
```

#### 方式二：使用 HTML 幻灯片（推荐！无需 PPT）
```bash
# 1. 准备一个 JSON 配置文件（参考 example_slides.json）

# 2. 创建项目
python main.py create "HTML 演示"

# 3. 导入 JSON（自动生成 HTML 并渲染为图片）
python main.py import-html example_slides.json --project "HTML 演示"

# 4. 生成音频和视频
python main.py run-all --project "HTML 演示"
```

#### 使用 HTML 幻灯片的优势
- ✅ 无需安装 PPT 或 LibreOffice
- ✅ 完全可控样式（可自定义 CSS）
- ✅ 支持代码高亮、LaTeX 公式等
- ✅ 跨平台渲染一致
- ✅ Git 友好，易于版本管理
- ✅ **支持多种内置模板和自定义模板**

## 项目结构

```
CourseVideoGen/
├── main.py                  # 命令行入口
├── requirements.txt         # 依赖列表
├── example_slides.json      # HTML 幻灯片示例
├── core/                    # 核心模块
│   ├── project_manager.py   # 项目管理
│   ├── ppt_parser.py        # PPT 解析
│   ├── html_generator.py    # HTML 幻灯片生成/渲染
│   ├── audio_generator.py   # 音频生成
│   └── video_generator.py   # 视频生成
├── models/                  # 数据模型
│   └── project.py
├── workspace/               # 项目数据目录
│   └── <项目名>/
│       ├── project.json
│       ├── slides/          # 幻灯片图片
│       ├── html/            # HTML 源文件
│       ├── scripts/         # 讲解稿
│       ├── audios/          # 生成的音频
│       └── output.mp4       # 最终视频
└── image_to_video.py        # (旧版) 简单图片转视频
```

## 命令行参数

### 全局命令

| 命令 | 说明 |
|-----|-----|
| `list` | 列出所有项目 |
| `create <name>` | 创建新项目 |
| `load <name>` | 加载项目 |

### 项目操作

| 命令 | 说明 | 选项 |
|-----|-----|-----|
| `import-ppt <file>` | 导入 PPT | `--project <项目名>` |
| `generate-audio` | 生成音频 | `--project <项目名>`, `--voice <发音人>` |
| `generate-video` | 生成视频 | `--project <项目名>`, `--output <文件名>` |
| `run-all` | 一键生成 | 同上 |

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
python main.py generate-audio --project my_project --voice zh-CN-YunxiNeural
```

## 示例工作流

假设你有一份 `course.pptx`：

```bash
# 1. 创建项目
python main.py create "Python入门课"

# 2. 导入 PPT（会自动提取每页文本作为讲解稿）
python main.py import-ppt course.pptx --project "Python入门课"

# 3. 查看和编辑讲解稿
# ls workspace/Python入门课/scripts/
# edit workspace/Python入门课/scripts/slide_01.txt

# 4. 生成音频和视频
python main.py run-all --project "Python入门课"

# 5. 找到最终视频
ls workspace/Python入门课/output.mp4
```

## 技术栈

- **python-pptx**: PPTX 解析
- **Pillow**: 图像处理
- **edge-tts**: 微软语音合成
- **moviepy**: 视频合成 (使用 1.x 版本，2.x API 不兼容)
- **mutagen**: 读取音频文件元数据和时长
- **pywin32**: (Windows 可选) PowerPoint COM，完美渲染 PPT
- **LibreOffice**: (跨平台可选) PPT 渲染

## 常见问题

### Q: PPT 转图片不清晰？

A: 不同平台有不同的最优方案：

**Windows (推荐):**
```bash
pip install pywin32
```
使用 pywin32 调用本机 PowerPoint，渲染效果最好，完美还原所有排版、字体、动画。

**Linux/macOS:**
```bash
# Ubuntu/Debian
apt update && apt install -y libreoffice

# macOS
brew install libreoffice
```
使用 LibreOffice 渲染。

如果都没有安装，会使用保底模式：提取 PPT 文本，生成简单的占位图。

### Q: 如何调整语速？

A: 可以在 `core/audio_generator.py` 中调整 `rate` 参数，例如 `rate="+10%"` 或 `rate="-10%"`。

### Q: 支持哪些视频格式？

A: 默认输出 `.mp4` (H.264 + AAC)，兼容性最好。

### Q: 每一页 PPT 的显示时长是如何确定的？

A: 每一页的显示时长等于该页讲解音频的实际时长。系统会使用 `mutagen` 库自动读取 MP3 文件的实际时长，确保语音播放与幻灯片显示完美同步。

### Q: 发现时长不对，如何修复已有项目的音频时长？

A: 使用提供的修复脚本：
```bash
python fix_duration.py "项目名称"
```
该脚本会重新读取所有音频文件的实际时长，并更新 project.json。

## 技术栈

## HTML 幻灯片 JSON 格式

```json
{
    "title": "课程标题",
    "theme": "light",      // 或 "dark"
    "template": "default",  // 模板名称 (见下文)
    "slides": [
        {
            "title": "第 1 页标题",
            "subtitle": "副标题（可选）",
            "content": "内容，可以是字符串或列表",
            "script": "这一页的讲解稿（可选）"
        }
    ]
}
```

## 使用模板

### 查看可用模板
```bash
python main.py list-templates
```

### 指定模板导入
```bash
python main.py create "我的课程"
python main.py import-html example_slides.json --template minimal --project "我的课程"
python main.py run-all --project "我的课程"
```

### 内置模板

- **default**: 默认模板，简洁干净
- **minimal**: 极简风格，现代设计
- **dark**: 深色主题，渐变背景
- **code**: 代码主题，适合编程课程

### 创建自定义模板

在项目的 `templates/` 目录下创建以下文件：

1. `mytemplate.html` - 主 HTML 模板
2. `_mytemplate_slide.html` - 单页幻灯片模板
3. `mytemplate.json` - 颜色配置

模板变量：
- `{title}` - 课程标题
- `{bg_color}` - 背景颜色
- `{text_color}` - 文字颜色
- `{accent_color}` - 强调色
- `{slides_html}` - 幻灯片内容（主模板）
- `{index}` - 当前页码（单页模板）
- `{total}` - 总页数（单页模板）
- `{content}` - 幻灯片内容（单页模板）

示例见项目 `templates/` 目录。

内容支持两种格式：

```json
// 格式 1: 字符串
"content": "一行简单的文本"

// 格式 2: 列表（自动渲染为 <ul>）
"content": [
    "第一项",
    "第二项",
    "第三项"
]
```

完整示例见 `example_slides.json`。

## 后续计划

- [ ] Web UI (Gradio/Streamlit)
- [ ] 自动生成字幕 (.srt)
- [ ] 视频转场效果
- [ ] 音频预览功能
- [ ] 视频模板系统
- [ ] 更多 HTML 幻灯片主题
- [ ] 支持 Markdown 导入

## License

MIT

