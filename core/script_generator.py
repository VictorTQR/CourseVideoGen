import os
import json
from typing import List, Dict
from models.project import Project, Slide
from core.llm import LLMConfig, call_llm, extract_json

OVERVIEW_SYSTEM_PROMPT = """你是一名经验丰富的教学视频讲解稿策划助手。
请根据用户提供的课程幻灯片内容，生成一份结构化的课程概览。

严格要求：
1. 输出必须是合法的 JSON
2. 只输出 JSON 本身，不要输出 Markdown 代码块标记或解释文字
3. 所有字符串使用中文

JSON 结构：
{
  "course_summary": "课程整体概述",
  "target_audience": "目标听众",
  "tone": "讲解语气风格",
  "slide_overview": [
    {"id": 1, "topic": "该页主题", "key_points": ["要点1", "要点2"]}
  ]
}"""

SCRIPT_SYSTEM_PROMPT = """你是一名教学视频讲解稿撰写助手。
请根据课程概览和当前页幻灯片内容，撰写一段口语化的讲解稿。

课程概览：
{overview_json}

要求：
1. 语言口语化，自然流畅，像在给学生讲课
2. 长度适中，一段话即可（约100-300字）
3. 可以适当使用"上一页我们讲了..."、"接下来..."等衔接语
4. 不要使用"大家好"等开场白（除非是第1页）
5. 直接输出讲解稿文本，不要加标题或格式标记"""

def generate_overview(project: Project, config: LLMConfig) -> Dict:
    """Phase 1: 生成课程概览

    读取所有 slide.content，调用 LLM 生成结构化课程概览 JSON。
    结果写入 project.overview 并保存。
    """
    user_text = f"课程名称：{project.name}\n幻灯片内容：\n"
    for i, slide in enumerate(project.slides):
        user_text += f"---第{i+1}页---\n{slide.content}\n"

    response = call_llm(OVERVIEW_SYSTEM_PROMPT, user_text, config)
    overview = extract_json(response)
    project.overview = overview
    return overview

def generate_scripts(project: Project, config: LLMConfig, project_dir: str) -> List[str]:
    """Phase 2: 逐页生成讲解稿

    遍历每页 slide，调用 LLM 生成口语化讲解稿。
    写入 scripts/slide_XX.txt 并自动回写 slide.script。
    单页失败不影响其他页。
    """
    scripts_dir = os.path.join(project_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    overview_json = ""
    if project.overview:
        overview_json = json.dumps(project.overview, ensure_ascii=False)

    system_prompt = SCRIPT_SYSTEM_PROMPT.format(overview_json=overview_json)
    saved_paths = []

    for slide in project.slides:
        user_text = f"课程名称：{project.name}\n幻灯片内容：\n{slide.content}"
        script = None
        for attempt in range(2):
            try:
                response = call_llm(system_prompt, user_text, config)
                script = response.strip()
                break
            except Exception as e:
                if attempt == 0:
                    print(f"[WARN] 第 {slide.id} 页生成失败，重试中...")
                    continue
                print(f"[ERROR] 第 {slide.id} 页生成失败: {e}")
                break

        if script:
            filename = f"slide_{slide.id:02d}.txt"
            filepath = os.path.join(scripts_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(script)
            saved_paths.append(filepath)
            slide.script = script

    return saved_paths