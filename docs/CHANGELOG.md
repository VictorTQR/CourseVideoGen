# 变更日志

所有重要的项目变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 新增五阶段完整工作流：`create` → `import` → `script generate` → `generate-audio` → `generate-video`
- 新增 `core/llm.py` 模块：LLM 配置与调用，支持 OpenAI 兼容 API
- 新增 `core/script_generator.py` 模块：自动生成课程讲解稿和概览
- 新增 `script generate` 命令：调用 LLM 生成讲解稿
- 新增 `script apply` 命令：将 scripts/*.txt 回写 project.json

### 变更
- `project.json` 新增 `content`（幻灯片文本）、`overview`（课程概览）字段
- `Slide` 数据模型新增 `content` 字段

### 移除
- 移除 HTML 幻灯片生成能力（JSON → HTML），由上游 CoursePPTGen 负责
- 移除 `HTMLSlideGenerator` 类和 `BUILTIN_TEMPLATES` 内置模板
- 移除 `templates/` 目录（chemistry / custom 模板）
- 移除 `examples/` 目录（示例 JSON 文件）
- 移除 `import-html` 的 JSON 导入模式、`--template` / `--theme` 选项
- 移除 `list-templates` 命令
- 移除 `tests/test_template.py`

### 新增
- `import-html` 改为直接接收 HTML 文件（Playwright 截图渲染）
- 创建 docs 目录，整理项目文档

### 变更
- `core/html_generator.py` 精简为仅包含 `HTMLSlideRenderer`
- 项目定位明确为下游工具：接收图片（来自 PPTX/HTML）→ TTS → 视频

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
