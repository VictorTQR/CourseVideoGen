# 安装指南

## 环境要求

- Python 3.12 或更高版本
- 操作系统：Windows、macOS 或 Linux

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd CourseVideoGen
```

### 2. 安装依赖

使用 uv（推荐）：

```bash
uv sync
```

或使用 pip：

```bash
pip install -r requirements.txt
```

## 依赖说明

### 必需依赖

| 包名 | 说明 |
|------|------|
| moviepy<2.0 | 视频合成（2.x API 不兼容） |
| Pillow | 图像处理 |
| numpy | 数值计算 |
| python-pptx | PPTX 文本提取 |
| edge-tts | 微软语音合成 |
| mutagen | 音频元数据读取 |
| typer | CLI 框架 |
| loguru | 日志 |
| python-dotenv | 环境变量加载 |
| openai | LLM 调用（讲解稿生成） |

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

```bash
cvg --help
```

## LLM 配置

讲解稿生成需要 LLM API，默认使用智谱 GLM-4-Flash。

**方式一：环境变量**

```bash
# .env 文件或 shell
OPENAI_API_KEY="your-key"
OPENAI_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
CVG_MODEL="glm-4-flash"
```

**方式二：命令行参数**

```bash
cvg script generate -p "课" --api-key "your-key" --model "glm-4-flash"
```

优先级：CLI 参数 > 环境变量 > 默认值

## 常见问题

### Q: moviepy 安装失败？

确保安装的是 1.x 版本，已指定 `moviepy<2.0`。

### Q: Playwright 截图报错？

```bash
pip install playwright
playwright install chromium
```

### Q: script generate 报错缺少 openai 包？

openai 已包含在必需依赖中。如果使用虚拟环境，确保在正确的环境中安装。

## 下一步

查看 [README.md](../README.md) 了解使用方法。
