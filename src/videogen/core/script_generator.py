import os
import json
from typing import Dict
from videogen.models.project import Project, Slide
from videogen.core.llm import LLMConfig, call_llm, extract_json

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
2. 专注于讲解当前页的内容，不要回顾上一页或预告下一页
3. 长度适中，一段话即可（约100-300字）
4. 第 1 页用简短开场引入课程主题，最后一页用简短总结收尾
5. 直接输出讲解稿文本，不要加标题或格式标记"""

def generate_overview(project: Project, config: LLMConfig) -> Dict:
    """Phase 1: 生成课程概览

    读取所有 slide.content，调用 LLM 生成结构化课程概览 JSON。
    返回 overview dict，由调用方负责持久化。
    """
    user_text = f"课程名称：{project.name}\n幻灯片内容：\n"
    for i, slide in enumerate(project.slides):
        user_text += f"---第{i+1}页---\n{slide.content}\n"

    response = call_llm(OVERVIEW_SYSTEM_PROMPT, user_text, config)
    overview = extract_json(response)
    return overview

def generate_scripts(project: Project, config: LLMConfig, project_dir: str) -> Dict[int, str]:
    """Phase 2: 逐页生成讲解稿

    遍历每页 slide，调用 LLM 生成口语化讲解稿。
    写入 scripts/slide_XX.txt，返回 {slide_id: script_text} dict。
    由调用方负责将 script 持久化到 project.json。
    单页失败不影响其他页。
    """
    scripts_dir = os.path.join(project_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    overview_json = ""
    if project.overview:
        overview_json = json.dumps(project.overview, ensure_ascii=False)

    system_prompt = SCRIPT_SYSTEM_PROMPT.format(overview_json=overview_json)
    scripts_map = {}

    for slide in project.slides:
        total = len(project.slides)
        user_text = f"课程名称：{project.name}\n"
        user_text += f"当前：第 {slide.id} 页 / 共 {total} 页\n"
        if slide.id == 1:
            user_text += "这是课程的第一页，请用开场引入。\n"
        elif slide.id == total:
            user_text += "这是课程的最后一页，请用总结收尾。\n"
        user_text += f"\n当前页内容：\n{slide.content}"
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
            scripts_map[slide.id] = script

    return scripts_map