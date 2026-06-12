# CourseVideoGen 重构说明

## 1. 目标

将项目流程从三阶段重构为五阶段，新增 `script generate` 和 `script apply` 两个子命令。
核心思路：**导入阶段只提取原始内容（content），讲解稿（script）由 LLM 生成后用户确认再写入 project.json。**

## 2. 新流程总览

```
create          → project.json (空壳)
import          → slides/*.png, project.json { id, image, content }
script generate → scripts/*.txt + 自动回写 project.json { script }
                 （生成后自动 apply，用户确认满意就直接跑下一步）
script apply    → project.json { script } (可选，仅在用户编辑了 txt 后手动执行)
generate-audio  → audios/*.mp3, project.json { audio, duration }
generate-video  → output.mp4
```

**设计说明：** `script generate` 完成后自动将 txt 内容回写到 project.json，大多数情况下 LLM 生成的讲稿直接可用，不需要用户干预。`script apply` 是补救命令——只在用户编辑了 txt 后需要同步回 json 时手动调用。

## 3. Slide 字段变更

```python
# ===== 之前 =====
@dataclass
class Slide:
    id: int
    image: str              # 图片文件名
    script: str = ""        # 讲解稿（import 时直接填入 PPT 文本）
    audio: Optional[str] = None   # 音频文件名
    duration: float = 3.0          # 显示时长（秒）

# ===== 之后 =====
@dataclass
class Slide:
    id: int
    image: str                     # 图片文件名
    content: str = ""              # PPT/HTML 原始内容（导入阶段填入）
    script: Optional[str] = None   # 讲解稿（script apply 阶段填入）
    audio: Optional[str] = None    # 音频文件名（generate-audio 阶段填入）
    duration: Optional[float] = None  # 显示时长（generate-audio 阶段填入）
```

关键字段含义变化：
- **新增 `content`**：PPTX 提取的原始文本或 HTML 提取的文本，是 LLM 生成讲稿的依据
- **`script`**：从之前的"PPT 文本直接填入"改为"LLM 生成的口语化讲解稿"，默认值 `""` → `None`
- **`duration`**：默认值 `3.0` → `None`，只在 generate-audio 阶段写入真实值

`from_dict` 需要做兼容处理：如果旧项目 json 里没有 `content` 字段但有 `script` 字段，把 `script` 的值迁移到 `content`。

## 4. 各文件改动

### 4.1 models/project.py

- Slide dataclass 按上述变更
- `from_dict` 兼容旧格式（缺少 content 时从 script 迁移）

### 4.2 core/project_manager.py

- `add_slide()`：初始化时 `content=""`, `script=None`, `duration=None`
- `update_slide_script()`：**改名为 `update_slide_content()`**，更新 content 字段（导入阶段用）
- **新增 `apply_slide_script()`**：更新 script 字段（script apply 阶段用）
- `update_slide_audio()`：不变

### 4.3 core/ppt_parser.py

- 不改动。`get_slide_text()` 返回文本列表，由 main.py 调用后写入 content。
- 但建议把 `_extract_text_fallback()` 中的文本提取逻辑确认能正常返回文本。

### 4.4 core/html_generator.py

- `render_to_images()` 返回值需要扩展，除了图片列表，还需要返回每页的文本内容。
- 方式：在 Playwright 截图循环中，用 `page.evaluate()` 或 `slide_elem.text_content()` 提取当前可见 `.slide` 的纯文本。
- 返回类型从 `List[str]` 改为 `List[Tuple[str, str]]`，每个元素是 `(image_filename, text_content)`。
- 或者新增 `render_to_images_and_texts()` 方法，返回 `Dict[str, str]`（filename → text）。

### 4.5 core/audio_generator.py

- 不改动。`generate_audio()` 接收的 text 参数由 main.py 从 `slide.script` 传入。
- `_get_audio_duration()` 中保底返回值从 `3.0` 改为一个合理的最小值（如 `1.0`），因为现在 duration 不再有默认值 3.0。

### 4.6 core/video_generator.py

- `generate_final_video()` 中有一段"如果 duration 还是默认的 3.0 秒左右"的兜底逻辑，这段需要调整。
- 现在 `slide.duration` 来自 generate-audio 阶段写入的真实值，不应该有 3.0 的保底判断。
- 如果 `slide.duration` 为 None，应该抛异常而不是静默使用默认值。
- 或者保留安全检查，但把 `abs(duration - 3.0) < 0.1` 改为 `duration is None`。

### 4.7 新增 core/script_generator.py

新模块，负责 LLM 讲稿生成。

功能：
- 读取 project.json 中所有 slide 的 content
- 调用 LLM 生成口语化讲解稿
- 写入 scripts/slide_XX.txt

LLM 集成方式参考 CourseDocGen 项目的 LLM 集成四步法：
1. **配置链**：`CLI 参数 > 环境变量 > 默认值`，用 `resolve_llm_config()` 统一解析
2. **Prompt 设计**：system prompt 注入 content 作为上下文，要求生成口语化讲解稿
3. **多策略 JSON 提取**：依次尝试直接解析 → code block 提取 → 修复
4. **LLM 层独立模块化**：`llm.py` 作为独立模块

具体要求：
- 支持逐页生成和批量生成两种模式
- 每页生成独立，失败不影响其他页
- 输出到 `scripts/slide_XX.txt`，每个文件一个独立的讲解稿
- 生成完成后打印提示，提醒用户查看和编辑

CLI 参数设计（在 main.py 中暴露）：
- `--voice` / `--model`：指定 LLM 模型（默认值根据 CourseDocGen 的约定）
- `--base-url`：API 基础地址
- `--api-key`：API 密钥（优先级：CLI > 环境变量）

**注意**：LLM 相关依赖（openai 等）应为可选依赖，不在核心依赖中。未安装时给出提示。

### 4.8 main.py — 架构变更：移除进程内状态

**核心改动：删除 `self.current_project` 和 `self.project_dir`，所有命令通过 `--project` 参数指定项目，每次命令独立加载。**

之前的设计是 create/load 后在进程内持有状态，后续命令依赖这个状态。但 CLI 每次调用都是独立进程，状态无法跨命令保留，导致 import-ppt/import-html 必须和 create 在同一次调用中执行，否则报错。这是 bug。

**移除：**
- `CourseVideoGen.current_project` 属性
- `CourseVideoGen.project_dir` 属性
- `CourseVideoGen.load()` 方法
- `load` CLI 命令（`main.py list` 已能查看项目列表）

**统一模式：**
所有需要项目上下文的命令都接收 `--project` 参数，内部统一走 `_require_project(project_name)` 加载：

```python
def _require_project(self, project_name: str) -> tuple:
    """加载项目，返回 (project, project_dir)。项目不存在则报错退出。"""
    project = self.pm.load_project(project_name)
    if not project:
        print(f"[ERROR] 项目不存在: {project_name}")
        print('  使用 python main.py create "项目名" 创建')
        sys.exit(1)
    project_dir = self.pm.get_project_path(project_name)
    return project, project_dir
```

每个命令方法改为接收 `project_name` 参数，内部调用 `_require_project`：

```python
# 之前
def import_ppt(self, pptx_path: str):
    if not self.current_project:
        print("[ERROR] 请先创建或加载项目")
        sys.exit(1)
    parser = PPTParser(self.project_dir)
    ...

# 之后
def import_ppt(self, pptx_path: str, project_name: str):
    project, project_dir = self._require_project(project_name)
    parser = PPTParser(project_dir)
    ...
```

CLI 命令结构变更：

```
之前：
  create <name>, load <name>, list
  import-ppt <file>            ← 需要 create/load 后进程内状态
  import-html <file>           ← 同上
  generate-audio --project     ← 有 --project
  generate-video --project     ← 有 --project
  run-all --project            ← 有 --project

之后：
  create <name>, list
  import-ppt <file> --project <名>    ← 新增 --project
  import-html <file> --project <名>   ← 新增 --project
  script generate --project <名>      ← 有 --project
  script apply --project <名>         ← 有 --project
  generate-audio --project <名>       ← 不变
  generate-video --project <名>       ← 不变
  run-all --project <名>              ← 不变
```

所有需要项目的命令统一模式：
```python
elif args.command == "xxx":
    if not args.project:
        print("[ERROR] 请使用 --project 指定项目")
        sys.exit(1)
    app.xxx(..., args.project)
```

`create` 和 `list` 不需要项目，不动。

## 5. 项目工作目录结构

```
workspace/<项目名>/
├── project.json          # 项目元数据（唯一权威数据源）
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

## 6. 数据流向图

```
[import 阶段]
  PPTX/HTML → 提取文本 → slide.content (project.json)
             → 截图   → slide.image  (slides/*.png)

[script generate 阶段]
  slide.content (project.json) → LLM → scripts/*.txt → 自动回写 slide.script (project.json)
  （用户如需修改，编辑 scripts/*.txt 后执行 script apply）

[generate-audio 阶段]
  slide.script (project.json) → edge-tts → audios/*.mp3
                                              → slide.audio, slide.duration (project.json)

[generate-video 阶段]
  slide.image + slide.audio + slide.duration → moviepy → output.mp4
```

每个字段只被写一次，流向单行，无回环。

## 7. project.json 完整示例（重构后）

```json
{
    "name": "Python入门课",
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
    "updated_at": "2026-05-30T11:00:00"
}
```

## 8. 兼容性

- `from_dict` 需要兼容旧格式的 project.json（只有 script 没有 content 的情况）
- 兼容策略：如果 json 中有 `script` 但没有 `content`，把 `script` 值赋给 `content`，`script` 设为 `None`
- 这样旧项目重新执行 script generate → apply → generate-audio 即可继续

## 9. 不改的文件

- `core/audio_generator.py`：接口不变
- `core/video_generator.py`：接口不变（只需调整 duration 保底逻辑）
- `scripts/fix_duration.py`：保留，仍可用
- `scripts/image_to_video.py`：保留
- `tests/simple_test.py`、`tests/test_create_pptx.py`：保留

## 10. 后续文档更新

重构完成后需要同步更新：
- `README.md`：新流程说明、新命令文档
- `docs/API.md`：新模块和新命令
- `docs/CHANGELOG.md`：记录本次重构
- `docs/PRD.md`：更新流程图和功能需求
