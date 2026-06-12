# CourseVideoGen Script Generate 重构设计

**日期：** 2026-06-12
**状态：** 已批准

---

## 1. 概述

将项目流程从三阶段重构为五阶段，新增 `script generate` 和 `script apply` 两个子命令。核心思路：**导入阶段只提取原始内容（content），讲解稿（script）由 LLM 生成后用户确认再写入 project.json。**

## 2. 新流程总览

```
create          → project.json (空壳)
import          → slides/*.png, project.json { id, image, content }
script generate → scripts/*.txt + 自动回写 project.json { script, overview }
                  （生成后自动 apply，用户确认满意就直接跑下一步）
script apply    → project.json { script } (可选，仅在用户编辑了 txt 后手动执行)
generate-audio  → audios/*.mp3, project.json { audio, duration }
generate-video  → output.mp4
```

## 3. 数据模型变更

### 3.1 Slide dataclass

```python
@dataclass
class Slide:
    id: int
    image: str                     # 图片文件名
    content: str = ""              # PPT/HTML 原始内容（import 阶段填入）
    script: Optional[str] = None   # 讲解稿（script generate 阶段填入）
    audio: Optional[str] = None    # 音频文件名
    duration: Optional[float] = None  # 显示时长
```

字段含义变化：
- **新增 `content`**：PPTX/HTML 提取的原始文本，是 LLM 生成讲稿的依据
- **`script`**：从之前的"PPT 文本直接填入"改为"LLM 生成的口语化讲解稿"，默认值 `""` → `None`
- **`duration`**：默认值 `3.0` → `None`，只在 generate-audio 阶段写入真实值

### 3.2 Project dataclass

新增 `overview` 字段存储 Phase 1 生成的结构化概览：

```python
@dataclass
class Project:
    name: str
    slides: List[Slide]
    overview: Optional[Dict] = None  # 两阶段生成的课程概览
    created_at: str = ""
    updated_at: str = ""
```

`overview` JSON 结构：
```json
{
  "course_summary": "本课介绍 Python 基础语法...",
  "target_audience": "零基础编程入门者",
  "tone": "轻松易懂，适当使用比喻",
  "slide_overview": [
    {"id": 1, "topic": "Python简介", "key_points": ["通用语言", "简单易学"]}
  ]
}
```

### 3.3 兼容处理

`from_dict` 兼容旧格式：
- 缺少 `content` 但有 `script` → 将 `script` 值迁移到 `content`，`script` 设为 `None`
- 缺少 `overview` → `None`

## 4. LLM 模块 (core/llm.py)

### 4.1 设计原则

从 CourseDocGen 的 `llm.py` 适配，保持相同的配置解析和 JSON 提取模式。

### 4.2 LLMConfig

```python
@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float
```

### 4.3 resolve_llm_config()

优先级链：`CLI 参数 > 环境变量 > 默认值`

| 参数 | 环境变量 | 默认值 |
|------|---------|--------|
| api_key | `OPENAI_API_KEY` | 无（必填，缺失抛 ValueError） |
| base_url | `OPENAI_BASE_URL` | `https://open.bigmodel.cn/api/paas/v4` |
| model | `CVG_MODEL` | `glm-4-flash` |
| temperature | — | `0.7` |

环境变量名说明：
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` 遵循 OpenAI 兼容约定，换任何 OpenAI-compatible API 只需改这两个
- `CVG_MODEL` 是项目专用，避免和 CourseDocGen 的 `DOCGEN_MODEL` 冲突

### 4.4 call_llm()

```python
def call_llm(system_prompt: str, user_text: str, config: LLMConfig) -> str:
    """调用 LLM，返回原始文本响应。"""
    from openai import OpenAI  # 延迟导入
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    response = client.chat.completions.create(
        model=config.model,
        temperature=config.temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
    )
    return response.choices[0].message.content
```

注意：与 CourseDocGen 不同，这里返回 `str` 而不是 `dict`，因为讲解稿是纯文本而非 JSON。

### 4.5 extract_json()

从 CourseDocGen 复制，3 策略提取（fenced block → 直接解析 → 花括号兜底）。

### 4.6 openai 依赖

作为可选依赖：`pyproject.toml` 中 `[project.optional-dependencies] llm = ["openai>=1.0.0"]`。未安装时 `call_llm()` 捕获 `ImportError` 并给出安装提示。

## 5. Script Generator (core/script_generator.py)

### 5.1 两阶段生成流程

```
Phase 1: generate_overview(project, config) → overview dict
  - 拼装所有 slide.content 为 user_text
  - system prompt 要求输出结构化 JSON 概览
  - 调用 call_llm() + extract_json()
  - 写入 project.overview，保存 project.json

Phase 2: generate_scripts(project, config) → List[str] (文件路径)
  - 遍历每页 slide
  - system prompt = 角色说明 + project.overview JSON + 生成规则
  - user_text = 当前页的 slide.content
  - 调用 call_llm()，返回纯文本讲解稿
  - 写入 scripts/slide_XX.txt
  - 自动回写 slide.script（静默 apply）
  - 单页失败不影响其他页，打印错误继续
```

### 5.2 Phase 1 Prompt 设计

**System prompt：**
```
你是一名经验丰富的教学视频讲解稿策划助手。
请根据用户提供的课程幻灯片内容，生成一份结构化的课程概览。

严格要求：
1. 输出必须是合法的 JSON
2. 只输出 JSON 本身，不要输出 Markdown 代码块标记或解释文字
3. 所有字符串使用中文

JSON 结构：
{
  "course_summary": "课程整体概述",
  "target_audience": "目标听众",
  "tone": "讲解语气风格",
  "slide_overview": [
    {"id": 1, "topic": "该页主题", "key_points": ["要点1", "要点2"]}
  ]
}
```

**User text：**
```
课程名称：{project.name}
幻灯片内容：
---第1页---
{slide_1.content}
---第2页---
{slide_2.content}
...
```

### 5.3 Phase 2 Prompt 设计

**System prompt：**
```
你是一名教学视频讲解稿撰写助手。
请根据课程概览和当前页幻灯片内容，撰写一段口语化的讲解稿。

课程概览：
{overview_json}

要求：
1. 语言口语化，自然流畅，像在给学生讲课
2. 长度适中，一段话即可（约100-300字）
3. 可以适当使用"上一页我们讲了..."、"接下来..."等衔接语
4. 不要使用"大家好"等开场白（除非是第1页）
5. 直接输出讲解稿文本，不要加标题或格式标记
```

**User text：** 当前页的 `slide.content`

### 5.4 重试策略

每页生成失败时最多重试 1 次，仍失败则跳过并打印错误。

## 6. CLI 命令结构

```
create, load, list
import-ppt, import-html
script generate [--model] [--base-url] [--api-key]   ← 新增子命令组
script apply                                          ← 新增子命令组
generate-audio, generate-video, run-all
```

`script` 是 argparse 子命令组，下设 `generate` 和 `apply` 两个子命令。

## 7. 各文件改动

### 7.1 models/project.py

- Slide dataclass 字段变更（content 新增，script/duration 改为 None 默认）
- Project dataclass 新增 overview 字段
- `from_dict` 兼容旧格式

### 7.2 core/project_manager.py

- `add_slide()`：初始化 `content=""`, `script=None`, `duration=None`
- `update_slide_script()` → 改名为 `update_slide_content()`
- 新增 `apply_slide_script()`：更新 script 字段
- 新增 `update_overview()`：更新 project.overview

### 7.3 core/ppt_parser.py

- 不改动。`get_slide_text()` 返回文本列表，由 main.py 调用后写入 content。

### 7.4 core/html_generator.py

- `render_to_images()` 返回值从 `List[str]` 改为 `List[Tuple[str, str]]`，即 `[(image_filename, text_content), ...]`
- 截图循环中用 `page.evaluate()` 或 `slide_elem.text_content()` 提取当前可见 `.slide` 的纯文本

### 7.5 core/audio_generator.py

- 不改动。`generate_audio()` 接收的 text 参数由 main.py 从 `slide.script` 传入。
- `_get_audio_duration()` 中保底返回值从 `3.0` 改为 `1.0`

### 7.6 core/video_generator.py

- `slide.duration` 为 `None` 时抛异常，不再静默使用默认值
- 移除 `abs(duration - 3.0) < 0.1` 的旧保底判断

### 7.7 新增 core/llm.py

- `LLMConfig` dataclass
- `resolve_llm_config()`
- `call_llm()`
- `extract_json()`

### 7.8 新增 core/script_generator.py

- `generate_overview()`
- `generate_scripts()`

### 7.9 main.py

- `import-ppt`：文本写入 `slide.content`，删除 scripts 目录写入逻辑
- `import-html`：`render_to_images()` 解包后文本写入 `slide.content`
- `script generate` 子命令：调用 script_generator 的两阶段生成
- `script apply` 子命令：遍历 scripts/ 目录，回写 project.json
- 修复 `import-ppt` 命令的加载逻辑 bug

## 8. 项目工作目录结构

```
workspace/<项目名>/
├── project.json          # 项目元数据（含 overview + slides）
├── slides/               # 幻灯片图片 (import 阶段产出)
│   ├── slide_01.png
│   └── slide_02.png
├── scripts/              # 讲解稿 (script generate 阶段产出，用户可编辑)
│   ├── slide_01.txt
│   └── slide_02.txt
├── audios/               # 音频文件 (generate-audio 阶段产出)
│   ├── audio_01.mp3
│   └── audio_02.mp3
└── output.mp4            # 最终视频 (generate-video 阶段产出)
```

## 9. 数据流向图

```
[import 阶段]
  PPTX/HTML → 提取文本 → slide.content (project.json)
             → 截图   → slide.image  (slides/*.png)

[script generate 阶段 - Phase 1]
  所有 slide.content → LLM → project.overview (结构化大纲)

[script generate 阶段 - Phase 2]
  slide.content + overview → LLM → scripts/*.txt → 自动回写 slide.script (project.json)
  （用户如需修改，编辑 scripts/*.txt 后执行 script apply）

[generate-audio 阶段]
  slide.script (project.json) → edge-tts → audios/*.mp3
                                              → slide.audio, slide.duration (project.json)

[generate-video 阶段]
  slide.image + slide.audio + slide.duration → moviepy → output.mp4
```

每个字段只被写一次，流向单行，无回环。

## 10. project.json 完整示例

```json
{
    "name": "Python入门课",
    "overview": {
        "course_summary": "本课介绍 Python 基础语法...",
        "target_audience": "零基础编程入门者",
        "tone": "轻松易懂，适当使用比喻",
        "slide_overview": [
            {"id": 1, "topic": "Python简介", "key_points": ["通用语言", "简单易学"]}
        ]
    },
    "slides": [
        {
            "id": 1,
            "image": "slide_01.png",
            "content": "Python简介\n- 通用编程语言\n- 简单易学",
            "script": "大家好，今天我们来学习 Python 编程语言。Python 是一种通用编程语言，以简单易学著称...",
            "audio": "audio_01.mp3",
            "duration": 12.5
        }
    ],
    "created_at": "2026-05-30T10:00:00",
    "updated_at": "2026-06-12T11:00:00"
}
```

## 11. 兼容性

- `from_dict` 兼容旧格式的 project.json（只有 script 没有 content 的情况）
- 兼容策略：如果 json 中有 `script` 但没有 `content`，把 `script` 值赋给 `content`，`script` 设为 `None`
- 这样旧项目重新执行 script generate → apply → generate-audio 即可继续

## 12. 不改的文件

- `core/audio_generator.py`：接口不变
- `core/video_generator.py`：接口不变
- `scripts/fix_duration.py`：保留
- `scripts/image_to_video.py`：保留
- `tests/simple_test.py`、`tests/test_create_pptx.py`：保留

## 13. 后续文档更新

重构完成后需要同步更新：
- `README.md`：新流程说明、新命令文档
- `docs/API.md`：新模块和新命令
- `docs/CHANGELOG.md`：记录本次重构
- `docs/PRD.md`：更新流程图和功能需求
