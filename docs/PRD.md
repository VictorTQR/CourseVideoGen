# CourseVideoGen - PPT 讲解视频自动生成工具

**版本：** v0.1.1  
**日期：** 2026-04-26  
**作者：** ArkClaw  
**更新：** 2026-05-30 — 移除 HTML 幻灯片生成能力，定位为下游视频合成工具

---

## 1. 产品概述

### 1.1 产品定位
一款自动化工具（下游），将 PPT/HTML 幻灯片和讲解稿合成为带有讲解音频的教学/演示视频。

> **上游工具：** HTML 幻灯片的生成由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责。

### 1.2 目标用户
- 教师、培训师
- 内容创作者
- 需要制作教程视频的职场人士

### 1.3 解决的痛点
- PPT 录屏麻烦且不清晰
- 后期配音耗时耗力
- 需要专业的视频编辑技能

---

## 2. 功能需求

### 2.1 核心功能

| 功能模块 | 功能描述 | 优先级 |
|---------|---------|--------|
| **PPTX 解析** | 支持 .pptx 文件渲染为图片 | P0 |
| **HTML 渲染** | 支持 HTML 幻灯片文件渲染为图片（Playwright） | P0 |
| **讲解稿管理** | 用户可为每页幻灯片输入/编辑讲解文本 | P0 |
| **语音生成** | 使用 TTS 自动为每页讲解稿生成音频 | P0 |
| **视频合成** | 将图片 + 音频合成为最终视频 | P0 |
| **项目管理** | 保存和加载项目，支持继续编辑 | P1 |

### 2.2 已移除功能

以下功能已迁移至上游 CoursePPTGen：

| 功能 | 迁移说明 |
|------|---------|
| HTML 幻灯片生成（JSON → HTML） | 由 CoursePPTGen 负责 |
| 内置模板系统（default/minimal/dark/code） | 由 CoursePPTGen 的 preset 系统负责 |
| 自定义模板 | 由 CoursePPTGen 负责 |

---

## 3. 产品流程

### 3.1 主流程图

```
┌──────────────────────┐
│  CoursePPTGen (上游)  │
│  JSON → HTML / PPTX  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  CourseVideoGen       │
│                      │
│  1. 导入素材          │
│     PPTX / HTML 文件  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  2. 素材 → 图片       │
│  (解析 / 截图)        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  3. 输入讲解稿        │  ← 用户输入
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  4. 生成音频 (TTS)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  5. 合成视频          │
│  图片 + 音频 → MP4    │
└──────────────────────┘
```

### 3.2 两种输入模式

**模式 A: PPTX 导入**
- 输入：.pptx 文件
- 渲染：pywin32 (Win) / LibreOffice (Linux/Mac) / 文本保底
- 输出：slide_01.png, slide_02.png, ...

**模式 B: HTML 导入**
- 输入：HTML 幻灯片文件（由 CoursePPTGen 生成）
- 渲染：Playwright 截图
- 输出：slide_01.png, slide_02.png, ...

---

## 4. 技术方案

### 4.1 技术选型

| 模块 | 技术方案 | 说明 |
|------|---------|------|
| PPT 解析 | `python-pptx` | 提取文本和布局 |
| PPT→图片 | `pywin32` (Windows) / `LibreOffice` (跨平台) | 渲染 PPT 为图片 |
| HTML→图片 | `Playwright` | 截图渲染 |
| TTS | `edge-tts` | 微软语音服务 |
| 视频处理 | `moviepy` 1.x | 视频合成与处理 |
| 音频元数据 | `mutagen` | 读取音频时长 |

### 4.2 项目结构

```
CourseVideoGen/
├── main.py                      # 入口文件
├── requirements.txt             # 依赖
│
├── core/                        # 核心模块
│   ├── ppt_parser.py           # PPTX 解析
│   ├── html_generator.py        # HTML → 图片截图
│   ├── audio_generator.py      # 音频生成
│   ├── video_generator.py      # 视频生成
│   └── project_manager.py      # 项目管理
│
├── models/                      # 数据模型
│   └── project.py
│
├── scripts/                     # 辅助脚本
│   ├── fix_duration.py
│   └── image_to_video.py
│
└── workspace/                   # 工作区
    └── {project_name}/
        ├── project.json
        ├── slides/             # 幻灯片图片
        ├── scripts/            # 讲解稿
        ├── audios/             # 音频文件
        └── output.mp4          # 最终视频
```

---

## 5. 用户使用流程

### 5.1 命令行使用

```bash
# 1. 创建新项目
python main.py create "我的课程"

# 2a. 导入 PPTX
python main.py import-ppt "lesson.pptx"

# 2b. 或导入 HTML（由 CoursePPTGen 生成）
python main.py import-html "slides.html"

# 3. 编辑讲解稿（或手动编辑 workspace/.../scripts/）

# 4. 生成音频和视频
python main.py run-all
```

### 5.2 后续规划

- v1.2：Web 界面 (Gradio/Streamlit)
- v1.3：字幕生成 (.srt)
- v1.4：视频转场效果

---

## 6. 风险与依赖

| 风险 | 应对方案 |
|------|---------|
| PPT 渲染在 Linux 下不稳定 | 提供多种渲染方案备选 |
| TTS 网络请求失败 | 本地缓存 + 重试机制 |
| 大文件处理慢 | 支持断点续传 |

---

## 7. 成功指标

- 10 分钟内完成一个 20 页 PPT 的视频生成
- 生成的视频清晰度 ≥ 1080p
- 用户操作步骤 ≤ 5 步
