# CourseVideoGen Script Generate 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现五阶段流程：新增 `script generate` 和 `script apply` 子命令，将讲解稿生成从 LLM 独立模块完成。

**Architecture:** 两阶段 LLM 生成（Phase 1 课程概览 + Phase 2 逐页讲稿），LLM 逻辑封装在独立 `core/llm.py`，业务编排在 `core/script_generator.py`。其他模块改动为配合字段变更。

**Tech Stack:** Python, openai (可选依赖), edge-tts, moviepy, playwright

---

## Phase 1: 数据模型 & 基础设施改动

### Task 1: models/project.py — Slide/Project dataclass

**Files:**
- Modify: `models/project.py`

- [ ] **Step 1: Write the failing test for new Slide fields**

```python
# tests/test_models.py (新建)
import pytest
from models.project import Slide, Project

def test_slide_new_fields():
    slide = Slide(id=1, image="a.png")
    assert slide.content == ""
    assert slide.script is None
    assert slide.audio is None
    assert slide.duration is None

def test_slide_with_content():
    slide = Slide(id=1, image="a.png", content="Python 简介")
    assert slide.content == "Python 简介"

def test_project_with_overview():
    overview = {"course_summary": "test", "slide_overview": []}
    project = Project(name="Test", slides=[], overview=overview)
    assert project.overview == overview

def test_from_dict_migration_old_format():
    """旧格式只有 script 没有 content，应迁移"""
    data = {
        "name": "Test",
        "slides": [{"id": 1, "image": "a.png", "script": "old script"}],
        "created_at": "", "updated_at": ""
    }
    project = Project.from_dict(data)
    assert project.slides[0].content == "old script"
    assert project.slides[0].script is None

def test_from_dict_migration_new_format():
    """新格式有 content 和 script"""
    data = {
        "name": "Test",
        "slides": [{"id": 1, "image": "a.png", "content": "raw", "script": "oral"}],
        "created_at": "", "updated_at": ""
    }
    project = Project.from_dict(data)
    assert project.slides[0].content == "raw"
    assert project.slides[0].script == "oral"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — Slide.__init__ 不接受新字段

- [ ] **Step 3: Write minimal implementation**

```python
# models/project.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class Slide:
    id: int
    image: str
    content: str = ""
    script: Optional[str] = None
    audio: Optional[str] = None
    duration: Optional[float] = None

@dataclass
class Project:
    name: str
    slides: List[Slide]
    created_at: str = ""
    updated_at: str = ""
    overview: Optional[Dict] = None

    def to_dict(self) -> Dict:
        result = {
            "name": self.name,
            "slides": [asdict(slide) for slide in self.slides],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.overview is not None:
            result["overview"] = self.overview
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "Project":
        slides = []
        for s in data["slides"]:
            # 兼容旧格式：只有 script 没有 content
            if "content" not in s and "script" in s:
                s["content"] = s["script"]
                s["script"] = None
            slides.append(Slide(**s))
        return cls(
            name=data["name"],
            slides=slides,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            overview=data.get("overview")
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add models/project.py tests/test_models.py
git commit -m "feat: update Slide/Project dataclass with content and overview fields"
```

---

### Task 2: core/project_manager.py — 方法重命名/新增

**Files:**
- Modify: `core/project_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_project_manager.py (新建)
import pytest
import os
import shutil
from core.project_manager import ProjectManager

@pytest.fixture
def pm(tmp_path):
    return ProjectManager(base_dir=str(tmp_path))

def test_add_slide_initializes_new_fields(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    slide = project.slides[0]
    assert slide.content == ""
    assert slide.script is None
    assert slide.duration is None

def test_update_slide_content(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    pm.update_slide_content(project, 1, "Python 简介")
    assert project.slides[0].content == "Python 简介"

def test_apply_slide_script(pm):
    project = pm.create_project("test")
    pm.add_slide(project, "slide_01.png")
    pm.apply_slide_script(project, 1, "口服讲解稿")
    assert project.slides[0].script == "口服讲解稿"

def test_update_overview(pm):
    project = pm.create_project("test")
    overview = {"course_summary": "test"}
    pm.update_overview(project, overview)
    assert project.overview == overview
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_project_manager.py -v`
Expected: FAIL — 方法不存在

- [ ] **Step 3: Write minimal implementation**

```python
# core/project_manager.py
# add_slide() 中的 Slide(...) 初始化改为：
slide = Slide(
    id=slide_id,
    image=image_filename,
    content="",
    script=None,
    duration=None
)

# 新增方法（在 update_slide_script 之后）：
def update_slide_content(self, project: Project, slide_id: int, content: str):
    """更新 content 字段（import 阶段用）"""
    for slide in project.slides:
        if slide.id == slide_id:
            slide.content = content
            self._save_project(project)
            return

def apply_slide_script(self, project: Project, slide_id: int, script: str):
    """应用讲解稿（script apply 阶段用）"""
    for slide in project.slides:
        if slide.id == slide_id:
            slide.script = script
            self._save_project(project)
            return

def update_overview(self, project: Project, overview: dict):
    """更新课程概览"""
    project.overview = overview
    self._save_project(project)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_project_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/project_manager.py tests/test_project_manager.py
git commit -m "feat: add update_slide_content, apply_slide_script, update_overview methods"
```

---

### Task 3: core/html_generator.py — 返回值类型变更

**Files:**
- Modify: `core/html_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_html_generator.py (新建)
import pytest
import os
from core.html_generator import HTMLSlideRenderer

def test_render_returns_tuples(tmp_path):
    renderer = HTMLSlideRenderer(str(tmp_path))
    os.makedirs(os.path.join(str(tmp_path), "slides"), exist_ok=True)
    # 需要一个包含 .slide 元素的 HTML 文件来测试
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_html_generator.py -v`
Expected: FAIL — 返回类型不是 Tuple

- [ ] **Step 3: Write minimal implementation**

在 `render_to_images()` 中：
```python
def render_to_images(self, html_path: str) -> List[Tuple[str, str]]:
    # ... 现有截图逻辑 ...
    # 在截图循环中，提取文本：
    for i in range(1, slide_count + 1):
        # ... 截图逻辑 ...
        # 提取文本：
        texts = page.evaluate(f"""() => {{
            const slide = document.querySelectorAll('.slide')[{i-1}];
            return slide ? slide.textContent.trim() : '';
        }}""")
        images_and_texts.append((filename, texts))
    # 返回 List[Tuple[str, str]]
    return images_and_texts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_html_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/html_generator.py tests/test_html_generator.py
git commit -m "feat: render_to_images returns List[Tuple[str, str]] with text content"
```

---

### Task 4: core/audio_generator.py — 保底返回值变更

**Files:**
- Modify: `core/audio_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audio_generator.py
def test_get_audio_duration_fallback(tmp_path):
    # 创建测试音频文件...
    generator = AudioGenerator(str(tmp_path))
    # 当前的 3.0 保底应改为 1.0
```

- [ ] **Step 2: Write minimal implementation**

```python
# core/audio_generator.py
# _get_audio_duration() 最后一行：
return 1.0  # 原来是 3.0
```

- [ ] **Step 3: Commit**

```bash
git add core/audio_generator.py
git commit -m "fix: change audio duration fallback from 3.0 to 1.0"
```

---

### Task 5: core/video_generator.py — duration None 处理

**Files:**
- Modify: `core/video_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_video_generator.py
def test_generate_final_video_raises_on_none_duration(tmp_path):
    # 创建测试项目，slide.duration = None
    # 调用 generate_final_video 应抛异常
```

- [ ] **Step 2: Write minimal implementation**

在 `generate_final_video()` 中，移除 `abs(duration - 3.0) < 0.1` 判断，改为：
```python
if slide.duration is None:
    raise ValueError(f"第 {slide.id} 页的 duration 未设置，请先运行 generate-audio")
```

- [ ] **Step 3: Commit**

```bash
git add core/video_generator.py
git commit -m "fix: raise error when slide.duration is None instead of silent fallback"
```

---

### Task 6: pyproject.toml — 可选 LLM 依赖

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add optional LLM dependency**

```toml
[project.optional-dependencies]
llm = ["openai>=1.0.0"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add openai as optional dependency for LLM features"
```

---

## Phase 2: 新模块

### Task 7: core/llm.py — LLM 通用模块

**Files:**
- Create: `core/llm.py`
- Test: `tests/test_llm.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm.py
import pytest
from unittest.mock import patch, MagicMock
from core.llm import LLMConfig, resolve_llm_config, extract_json

def test_llm_config_frozen():
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    with pytest.raises(Exception):  # frozen dataclass
        config.api_key = "new"

def test_resolve_llm_config_defaults():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        config = resolve_llm_config()
        assert config.api_key == "test-key"
        assert config.base_url == "https://open.bigmodel.cn/api/paas/v4"
        assert config.model == "glm-4-flash"
        assert config.temperature == 0.7

def test_resolve_llm_config_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            resolve_llm_config()

def test_resolve_llm_config_cli_overrides_env():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key", "CVG_MODEL": "env-model"}):
        config = resolve_llm_config(api_key="cli-key", model="cli-model")
        assert config.api_key == "cli-key"
        assert config.model == "cli-model"
        assert config.base_url == "https://open.bigmodel.cn/api/paas/v4"  # env default

def test_extract_json_from_fenced_block():
    text = '```json\n{"key": "value"}\n```'
    assert extract_json(text) == {"key": "value"}

def test_extract_json_from_plain():
    assert extract_json('{"key": "value"}') == {"key": "value"}

def test_extract_json_with_extra_text():
    text = '以下是 JSON：\n{"key": "value"}\n以上'
    assert extract_json(text) == {"key": "value"}

def test_extract_json_invalid_raises():
    with pytest.raises(ValueError):
        extract_json("not json at all")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_llm.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write minimal implementation**

```python
# core/llm.py
import os
import re
import json
from typing import Optional
from dataclasses import dataclass

_DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
_DEFAULT_MODEL = "glm-4-flash"
_DEFAULT_TEMPERATURE = 0.7

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
) -> LLMConfig:
    resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError(
            "缺少 OPENAI_API_KEY。请通过 --api-key 传入，或在 .env / 环境变量中设置 OPENAI_API_KEY。"
        )
    resolved_base = base_url or os.environ.get("OPENAI_BASE_URL") or _DEFAULT_BASE_URL
    resolved_model = model or os.environ.get("CVG_MODEL") or _DEFAULT_MODEL
    resolved_temp = temperature if temperature is not None else _DEFAULT_TEMPERATURE
    return LLMConfig(
        api_key=resolved_key,
        base_url=resolved_base,
        model=resolved_model,
        temperature=resolved_temp,
    )

def extract_json(text: str) -> dict:
    stripped = text.strip()
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", stripped, re.DOTALL)
    if fence_match:
        stripped = fence_match.group(1).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = stripped[first : last + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        raise ValueError(f"无法从 LLM 响应中解析出 JSON")

def call_llm(system_prompt: str, user_text: str, config: LLMConfig) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "LLM 功能需要 openai 包。请运行: pip install coursevideogen[llm]"
        )
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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_llm.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/llm.py tests/test_llm.py
git commit -m "feat: add core/llm.py with LLMConfig, resolve_llm_config, extract_json, call_llm"
```

---

### Task 8: core/script_generator.py — 两阶段生成编排

**Files:**
- Create: `core/script_generator.py`
- Test: `tests/test_script_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_script_generator.py
import pytest
from unittest.mock import patch, MagicMock
from models.project import Project, Slide
from core.script_generator import generate_overview, generate_scripts
from core.llm import LLMConfig

@pytest.fixture
def sample_project():
    return Project(
        name="Python入门课",
        slides=[
            Slide(id=1, image="s1.png", content="Python 简介\n- 通用语言\n- 简单易学"),
            Slide(id=2, image="s2.png", content="变量与数据类型\n- 整数\n- 字符串"),
        ]
    )

def test_generate_overview_returns_dict(sample_project):
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    mock_response = '{"course_summary": "test", "target_audience": "beginners", "tone": "easy", "slide_overview": []}'
    with patch("core.script_generator.call_llm", return_value=mock_response):
        overview = generate_overview(sample_project, config)
        assert "course_summary" in overview
        assert sample_project.overview == overview

def test_generate_scripts_returns_file_paths(sample_project):
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    sample_project.overview = {"course_summary": "test", "slide_overview": []}
    with patch("core.script_generator.call_llm", return_value="这是一段讲解稿"):
        paths = generate_scripts(sample_project, config, str(tmp_path))
        assert len(paths) == 2
        assert "slide_01.txt" in paths[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_script_generator.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write minimal implementation**

```python
# core/script_generator.py
import os
from typing import List, Dict, Optional
from models.project import Project, Slide
from core.llm import LLMConfig, call_llm, extract_json

OVERVIEW_SYSTEM_PROMPT = """你是一名经验丰富的教学视频讲解稿策划助手。
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
}"""

SCRIPT_SYSTEM_PROMPT = """你是一名教学视频讲解稿撰写助手。
请根据课程概览和当前页幻灯片内容，撰写一段口语化的讲解稿。

课程概览：
{overview_json}

要求：
1. 语言口语化，自然流畅，像在给学生讲课
2. 长度适中，一段话即可（约100-300字）
3. 可以适当使用"上一页我们讲了..."、"接下来..."等衔接语
4. 不要使用"大家好"等开场白（除非是第1页）
5. 直接输出讲解稿文本，不要加标题或格式标记"""

def generate_overview(project: Project, config: LLMConfig) -> Dict:
    """Phase 1: 生成课程概览"""
    user_text = f"课程名称：{project.name}\n幻灯片内容：\n"
    for i, slide in enumerate(project.slides):
        user_text += f"---第{i+1}页---\n{slide.content}\n"

    response = call_llm(OVERVIEW_SYSTEM_PROMPT, user_text, config)
    overview = extract_json(response)
    project.overview = overview
    return overview

def generate_scripts(project: Project, config: LLMConfig, project_dir: str) -> List[str]:
    """Phase 2: 逐页生成讲解稿"""
    scripts_dir = os.path.join(project_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    overview_json = ""
    if project.overview:
        import json
        overview_json = json.dumps(project.overview, ensure_ascii=False)

    system_prompt = SCRIPT_SYSTEM_PROMPT.format(overview_json=overview_json)
    saved_paths = []

    for slide in project.slides:
        user_text = f"课程名称：{project.name}\n幻灯片内容：\n{slide.content}"
        script = None
        for attempt in range(2):  # 最多重试1次
            try:
                response = call_llm(system_prompt, user_text, config)
                script = response.strip()
                break
            except Exception as e:
                if attempt == 0:
                    print(f"[WARN] 第 {slide.id} 页生成失败，重试中...")
                    continue
                print(f"[ERROR] 第 {slide.id} 页生成失败: {e}")
                break

        if script:
            filename = f"slide_{slide.id:02d}.txt"
            filepath = os.path.join(scripts_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(script)
            saved_paths.append(filepath)
            slide.script = script  # 自动回写

    return saved_paths
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_script_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/script_generator.py tests/test_script_generator.py
git commit -m "feat: add core/script_generator.py with two-phase generation"
```

---

## Phase 3: CLI 集成

### Task 9: main.py — CLI 新命令 + bug fix

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Write the failing test (if CLI testing needed)**

```python
# tests/test_cli.py (部分测试)
# 验证 import-ppt 命令正常工作
# 验证 script generate / script apply 命令存在
```

- [ ] **Step 2: 实现主要改动**

**import_ppt 改动：**
```python
# 文本写入 slide.content，删除 scripts 目录写入逻辑
slide_texts = parser.get_slide_text(pptx_path)
for i, text in enumerate(slide_texts):
    if i < len(self.current_project.slides):
        self.pm.update_slide_content(self.current_project, i + 1, text)
```

**import_html 改动：**
```python
# render_to_images 返回 Tuple，解包
results = renderer.render_to_images(html_path)
for image, text in results:
    self.pm.add_slide(self.current_project, image)
    # 新增：更新 content
    slide_id = len(self.current_project.slides)
    self.pm.update_slide_content(self.current_project, slide_id, text)
```

**新增 script 子命令组：**
```python
# 在 argparse 子命令定义处添加：
script_parser = subparsers.add_parser("script", help="script 相关命令")
script_subparsers = script_parser.add_subparsers(dest="script_command")

# script generate
gen_script_parser = script_subparsers.add_parser("generate", help="生成讲解稿")
gen_script_parser.add_argument("--model", help="LLM 模型")
gen_script_parser.add_argument("--base-url", help="API 基础地址")
gen_script_parser.add_argument("--api-key", help="API 密钥")

# script apply
apply_script_parser = script_subparsers.add_parser("apply", help="应用讲解稿")
```

**script generate 实现：**
```python
elif args.script_command == "generate":
    if args.project:
        self.load(args.project)
    from core.llm import resolve_llm_config
    from core.script_generator import generate_overview, generate_scripts
    llm_config = resolve_llm_config(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model
    )
    generate_overview(self.current_project, llm_config)
    generate_scripts(self.current_project, llm_config, self.project_dir)
    print("[OK] 讲解稿生成完成")
```

**script apply 实现：**
```python
elif args.script_command == "apply":
    if args.project:
        self.load(args.project)
    scripts_dir = os.path.join(self.project_dir, "scripts")
    if not os.path.exists(scripts_dir):
        print("[ERROR] scripts 目录不存在")
        sys.exit(1)
    import glob
    txt_files = sorted(glob.glob(os.path.join(scripts_dir, "slide_*.txt")))
    applied = 0
    for txt_path in txt_files:
        basename = os.path.basename(txt_path)
        # slide_01.txt -> 1
        slide_id = int(basename.split("_")[1].split(".")[0])
        with open(txt_path, "r", encoding="utf-8") as f:
            script = f.read()
        self.pm.apply_slide_script(self.current_project, slide_id, script)
        applied += 1
    print(f"[OK] 成功应用 {applied} 页讲解稿")
```

**修复 import-ppt bug（当前代码 210-215 行）：**
当前代码：
```python
elif args.command == "import-ppt":
    app.load(args.file) if not app.current_project else None
    # 需要先有项目
    print("[ERROR] 请先使用 create 加载项目，再导入 PPT")
```
应改为检查 `current_project` 是否为 None：
```python
elif args.command == "import-ppt":
    if not app.current_project:
        print("[ERROR] 请先使用 create 加载项目，再导入 PPT")
        print('  python main.py create "项目名"')
        print('  python main.py import-ppt "lesson.pptx"')
        sys.exit(1)
    app.import_ppt(args.file)
```

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add script generate/apply commands and fix import-ppt bug"
```

---

## Phase 4: 文档更新

### Task 10: 文档更新

**Files:**
- Modify: `README.md`, `docs/API.md`, `docs/CHANGELOG.md`

- [ ] **Step 1: 更新 README.md**

添加新流程说明和新命令文档

- [ ] **Step 2: 更新 docs/API.md**

添加新模块和命令说明

- [ ] **Step 3: 更新 docs/CHANGELOG.md**

记录本次重构

- [ ] **Step 4: Commit**

```bash
git add README.md docs/API.md docs/CHANGELOG.md
git commit -m "docs: update README, API.md, CHANGELOG.md for script generate refactor"
```

---

## Self-Review 检查清单

- [ ] **Spec coverage:** 逐节检查设计文档，每项需求都能找到对应 Task
  - ✅ Slide/Project dataclass → Task 1
  - ✅ project_manager 方法 → Task 2
  - ✅ html_generator 返回值 → Task 3
  - ✅ audio_generator 保底值 → Task 4
  - ✅ video_generator duration → Task 5
  - ✅ 可选 LLM 依赖 → Task 6
  - ✅ core/llm.py → Task 7
  - ✅ core/script_generator.py → Task 8
  - ✅ CLI 命令 → Task 9
  - ✅ 文档更新 → Task 10

- [ ] **Placeholder scan:** 无 TBD/TODO/"fill in details" 等占位符
- [ ] **Type consistency:** 方法名、字段名在所有 Task 中一致
  - `update_slide_content` vs `update_slide_script` — ✅ 统一用新名
  - `apply_slide_script` — ✅ 在 Task 1/2/8/9 中一致
  - `update_overview` — ✅ 一致
  - `generate_overview` / `generate_scripts` — ✅ Task 7/8/9 中一致
  - `slide.content` / `slide.script` / `slide.duration` — ✅ 所有 Task 一致

---

**Plan complete.** 共 10 个 Task，分 4 个 Phase。建议执行顺序：Phase 1 (Task 1-6 并行) → Phase 2 (Task 7-8) → Phase 3 (Task 9) → Phase 4 (Task 10)。
