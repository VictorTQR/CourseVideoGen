# 文档目录

欢迎使用 CourseVideoGen 文档！

## 快速链接

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 使用说明 |
| [INSTALL.md](./INSTALL.md) | 安装指南 |
| [API.md](./API.md) | API 参考 |
| [CHANGELOG.md](./CHANGELOG.md) | 变更日志 |
| [PRD.md](./PRD.md) | 产品需求文档 |
| [REFACTOR_SPEC.md](./REFACTOR_SPEC.md) | 重构说明 |

## 项目概述

CourseVideoGen 是讲解视频自动生成的**下游工具**：

- 从 PPTX / HTML 导入幻灯片（渲染为图片）
- LLM 自动生成口语化讲解稿
- Edge-TTS 语音合成
- moviepy 合成视频

> **上游：** HTML 幻灯片生成由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责。
