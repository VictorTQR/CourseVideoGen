# 变更日志

所有重要的项目变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 创建 docs 目录，整理项目文档
- 新增 INSTALL.md - 详细安装指南
- 新增 API.md - API 参考文档
- 新增 CHANGELOG.md - 变更日志

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
- HTML 幻灯片支持
- Edge-TTS 语音合成
- 视频合成功能
- 项目管理功能
- 自定义模板系统

[未发布]: https://github.com/yourusername/CourseVideoGen/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/yourusername/CourseVideoGen/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/CourseVideoGen/releases/tag/v0.1.0
