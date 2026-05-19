# 模板系统文档

## 目录结构

```
templates/
├── README.md                  # 本文档
├── custom/                    # 自定义模板示例
│   ├── template.html          # 主HTML模板
│   ├── slide.html             # 单页幻灯片模板
│   └── config.json            # 配置文件
└── chemistry/                 # 化工学院模板
    ├── template.html
    ├── slide.html
    └── config.json
```

## 创建新模板

### 1. 创建目录结构
在 `templates/` 下创建新目录：
```
templates/my_template/
```

### 2. 添加必需文件

#### template.html - 主模板
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        /* 样式... */
    </style>
</head>
<body>
    {slides_html}
</body>
</html>
```

#### slide.html - 单页模板
```html
<div class="slide" id="slide-{index}">
    <div class="slide-title">{title}</div>
    <div class="slide-subtitle">{subtitle}</div>
    <div class="slide-content">{content}</div>
    <div class="slide-footer">{index} / {total}</div>
</div>
```

#### config.json - 配置
```json
{
    "light": {
        "bg_color": "#ffffff",
        "text_color": "#2d3748",
        "accent_color": "#667eea"
    },
    "dark": {
        "bg_color": "#1a202c",
        "text_color": "#f7fafc",
        "accent_color": "#90cdf4"
    }
}
```

### 3. 模板变量

| 变量 | 说明 |
|------|------|
| {title} | 项目/幻灯片标题 |
| {subtitle} | 副标题 |
| {content} | 内容 |
| {index} | 当前页码 |
| {total} | 总页数 |
| {bg_color} | 背景色 |
| {text_color} | 文本色 |
| {accent_color} | 强调色 |

### 4. 使用模板
```bash
python main.py create "我的项目"
python main.py import-html slides.json --template my_template --project "我的项目"
```

## 向后兼容性

系统同时支持旧的扁平化文件结构：
```
templates/
├── my_template.html
├── _my_template_slide.html
└── my_template.json
```
