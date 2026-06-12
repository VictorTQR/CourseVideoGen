# 安装指南

本文档介绍如何安装和配置 CourseVideoGen。

## 环境要求

- Python 3.12 或更高版本
- 操作系统：Windows、macOS 或 Linux

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd CourseVideoGen
```

### 2. 创建虚拟环境（推荐）

使用 Python venv：

```bash
python -m venv .venv
```

激活虚拟环境：

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. 安装依赖

使用 pip 安装：

```bash
pip install -r requirements.txt
```

或者使用 uv（推荐，更快）：

```bash
uv sync
```

## 依赖说明

### 必需依赖

| 包名 | 版本要求 | 说明 |
|------|----------|------|
| moviepy | <2.0 | 视频合成（2.x API 不兼容） |
| Pillow | >=10.0.0 | 图像处理 |
| numpy | >=1.24.0 | 数值计算 |
| python-pptx | >=0.6.21 | PPTX 文本提取 |
| edge-tts | >=6.1.0 | 微软语音合成 |
| mutagen | >=1.47.0 | 音频元数据读取 |

### 可选依赖

| 包名 | 说明 | 用途 |
|------|------|------|
| pywin32 | Windows 平台 | PPTX 完美渲染（推荐 Windows 用户安装） |
| playwright | HTML 幻灯片支持 | 将 HTML 渲染为图片截图 |

### 安装可选依赖

```bash
# Windows PPT 渲染（推荐）
pip install pywin32

# HTML 幻灯片截图
pip install playwright
playwright install chromium
```

## 验证安装

运行以下命令验证安装：

```bash
python main.py --help
```

应该看到命令行帮助信息。

## 常见安装问题

### Q: moviepy 安装失败？

A: 确保安装的是 1.x 版本，requirements.txt 中已指定 `moviepy<2.0`。

### Q: Windows 下 pywin32 安装问题？

A: 使用以下命令安装：

```bash
pip install pywin32
```

### Q: Playwright 截图报错？

A: 需要同时安装浏览器：

```bash
pip install playwright
playwright install chromium
```

### Q: 如何使用 uv 替代 pip？

A: 如果已安装 uv，可以直接运行：

```bash
uv sync
```

这会根据 pyproject.toml 安装所有依赖。

## 下一步

安装完成后，请查看 [README.md](../README.md) 了解如何使用 CourseVideoGen。
