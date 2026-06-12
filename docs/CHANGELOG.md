# 变更日志

所有重要的项目变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 新增 `core/llm.py` — LLM 配置解析、调用、JSON 提取（参考 CourseDocGen 四步法）
- 新增 `core/script_generator.py` — 两阶段讲解稿生成（课程概览 → 逐页讲稿）
- 新增 `script generate` 命令 — LLM 自动生成讲解稿，生成后自动回写 project.json
- 新增 `script apply` 命令 — 将编辑后的 scripts/*.txt 回写到 project.json
- 新增 `update_slide_content()` / `apply_slide_script()` / `update_overview()` 方法
- HTML 渲染器返回文本内容（`render_to_images` 返回 `List[Tuple[str, str]]`）
- Slide 新增 `content` 字段（PPT/HTML 原始内容），`overview` 字段（课程概览）

### 变更
- Slide 字段语义变更：`script` 从"PPT文本"改为"LLM生成的讲解稿"，默认值 `""` → `None`
- Slide 字段语义变更：`duration` 默认值 `3.0` → `None`，只在 generate-audio 阶段写入真实值
- CLI 从 argparse 迁移到 Typer + loguru
- 移除进程内状态（`current_project` / `project_dir`），所有命令通过 `--project` 指定项目
- 移除 `load` 命令，`list` 命令返回完整项目信息
- `import-ppt` 提取文本写入 `slide.content`（之前写入 `slide.script`）
- 音频时长保底值从 `3.0` 改为 `1.0`
- video_generator duration 为 None 时抛异常（不再静默使用默认值）

### 移除
- 移除 HTML 幻灯片生成能力（JSON → HTML），由上游 CoursePPTGen 负责
- 移除 `HTMLSlideGenerator` 类和 `BUILTIN_TEMPLATES` 内置模板
- 移除 `templates/` 目录（chemistry / custom 模板）
- 移除 `examples/` 目录（示例 JSON 文件）
- 移除 `import-html` 的 JSON 导入模式、`--template` / `--theme` 选项
- 移除 `list-templates` 命令
- 移除 `generate` 快捷命令

### 修复
- 修复 `list` 命令 TypeError：`list_projects()` 返回字符串列表但按字典访问

## [0.1.1] - 2026-04-27

### 修复
- **严重**: 修复音频时长获取问题，所有幻灯片不再被固定为 3 秒
- 修复 moviepy 版本兼容性问题，固定使用 1.x 版本（2.x API 不兼容）
- 修复 Windows 下 emoji 显示导致的编码错误

### 新增
- 添加 mutagen 依赖，专门用于读取音频元数据和时长
- 新增 fix_duration.py 脚本，支持修复已有项目的音频时长
- video_generator.py 添加安全检查，确保使用正确的音频时长

### 改进
- audio_generator.py 使用 mutagen 作为首选时长读取方式，moviepy 作为保底
- 更新 requirements.txt，添加 mutagen 和固定 moviepy 版本
- 更新 pyproject.toml 依赖配置
- 更新 README.md 文档

## [0.1.0] - 2026-04-27

### 新增
- 初始版本发布
- PPTX 解析为图片功能
- HTML 幻灯片生成与渲染
- Edge-TTS 语音合成
- 视频合成功能
- 项目管理功能
- 自定义模板系统

[未发布]: https://github.com/yourusername/CourseVideoGen/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/yourusername/CourseVideoGen/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/CourseVideoGen/releases/tag/v0.1.0
