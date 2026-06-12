# 文档目录

欢迎使用 CourseVideoGen 文档！

## 快速链接

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 主要使用说明 |
| [INSTALL.md](./INSTALL.md) | 详细安装指南 |
| [API.md](./API.md) | API 参考文档 |
| [CHANGELOG.md](./CHANGELOG.md) | 变更日志 |
| [PRD.md](./PRD.md) | 产品需求文档 |

## 快速开始

1. 查看 [INSTALL.md](./INSTALL.md) 了解如何安装
2. 阅读 [README.md](../README.md) 学习基本使用
3. 参考 [API.md](./API.md) 了解详细的模块和 API
4. 查看 [CHANGELOG.md](./CHANGELOG.md) 了解版本更新

## 项目概述

CourseVideoGen 是一个讲解视频自动生成工具（下游工具），负责：

- 从 PPTX 导入并渲染幻灯片
- 从 HTML 幻灯片渲染为图片（Playwright）
- 自动生成讲解音频（Edge-TTS）
- 合成图片+音频为视频
- 管理多个项目

> **上游：** HTML 幻灯片的生成由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责。

## 获取帮助

如果遇到问题，请查看：

1. 常见问题解答（见 README.md）
2. 变更日志了解最近更新（CHANGELOG.md）
3. 源码中的注释和文档
