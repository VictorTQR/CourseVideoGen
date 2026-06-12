# CourseVideoGen - PPT 讲解视频自动生成工具

**版本：** v0.2.0-dev
**作者：** ArkClaw
**更新：** 2026-06-12 — 重构为五阶段流程，新增 LLM 讲解稿生成，CLI 迁移到 Typer

---

## 1. 产品概述

### 1.1 产品定位
下游工具，将 PPT/HTML 幻灯片和讲解稿合成为带有讲解音频的教学/演示视频。

> **上游工具：** HTML 幻灯片生成由 [CoursePPTGen](https://github.com/yourusername/CoursePPTGen) 负责。

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
| **PPTX 解析** | PPTX 文件渲染为图片 | P0 |
| **HTML 渲染** | HTML 幻灯片渲染为图片（Playwright） | P0 |
| **讲解稿生成** | LLM 自动生成口语化讲解稿（两阶段） | P0 |
| **语音合成** | Edge-TTS 自动生成音频 | P0 |
| **视频合成** | 图片 + 音频合成为视频 | P0 |
| **项目管理** | 多项目管理，JSON 持久化 | P1 |

### 2.2 已移除功能

以下功能已迁移至上游 CoursePPTGen：

| 功能 | 说明 |
|------|------|
| HTML 幻灯片生成（JSON → HTML） | 由 CoursePPTGen 负责 |
| 内置模板系统 | 由 CoursePPTGen 的 preset 系统负责 |

---

## 3. 产品流程

### 3.1 五阶段流程

```
CoursePPTGen (上游)
    │
    ├── PPTX ──→ import-ppt
    └── HTML  ──→ import-html
                    │
                    ▼
              [1] create
              [2] import         → slides/*.png + content
              [3] script generate → scripts/*.txt + script（自动回写）
              [4] generate-audio  → audios/*.mp3 + audio + duration
              [5] generate-video  → output.mp4
```

### 3.2 script generate 两阶段

```
Phase 1: 读取所有 slide.content → LLM 生成课程概览 → project.overview
Phase 2: 逐页 slide.content + overview → LLM 生成讲解稿 → scripts/*.txt
         → 自动回写 project.json slide.script
```

单页失败重试 2 次后跳过，不影响其他页。

### 3.3 数据流向

```
import    → slide.content
script    → slide.script + scripts/*.txt + project.overview
audio     → slide.audio + slide.duration
video     → slide.image + slide.audio + slide.duration → output.mp4
```

每个字段只被写一次，流向单行，无回环。

---

## 4. 技术方案

| 模块 | 技术 | 说明 |
|------|------|------|
| CLI | Typer + loguru | 命令行框架 + 日志 |
| PPT 解析 | python-pptx | 提取文本 |
| PPT 渲染 | pywin32 / LibreOffice | PPTX → 图片 |
| HTML 渲染 | Playwright | HTML → 图片 |
| 讲解稿生成 | OpenAI API 兼容 | LLM 两阶段生成 |
| TTS | edge-tts | 语音合成 |
| 视频合成 | moviepy 1.x | 图片+音频 → MP4 |

---

## 5. 成功指标

- 10 分钟内完成一个 20 页 PPT 的视频生成
- 生成的视频清晰度 ≥ 1080p
- 用户操作步骤 ≤ 5 步
