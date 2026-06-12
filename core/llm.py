import os
import re
import json
from typing import Optional
from dataclasses import dataclass

_DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
_DEFAULT_MODEL = "glm-4-flash"
_DEFAULT_TEMPERATURE = 0.7

@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float

def resolve_llm_config(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> LLMConfig:
    """按 CLI 参数 > 环境变量 > 默认值 的优先级解析配置。"""
    resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError(
            "缺少 OPENAI_API_KEY。请通过 --api-key 传入，或在 .env / 环境变量中设置 OPENAI_API_KEY。"
        )
    resolved_base = base_url or os.environ.get("OPENAI_BASE_URL") or _DEFAULT_BASE_URL
    resolved_model = model or os.environ.get("CVG_MODEL") or _DEFAULT_MODEL
    resolved_temp = temperature if temperature is not None else _DEFAULT_TEMPERATURE
    return LLMConfig(
        api_key=resolved_key,
        base_url=resolved_base,
        model=resolved_model,
        temperature=resolved_temp,
    )

def extract_json(text: str) -> dict:
    """从 LLM 响应中提取 JSON。支持 3 种情况：纯 JSON、code block 包裹、纯文本中嵌 JSON。"""
    stripped = text.strip()
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", stripped, re.DOTALL)
    if fence_match:
        stripped = fence_match.group(1).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = stripped[first : last + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        raise ValueError(f"无法从 LLM 响应中解析出 JSON")

def call_llm(system_prompt: str, user_text: str, config: LLMConfig) -> str:
    """调用 LLM，返回原始文本响应。"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "LLM 功能需要 openai 包。请运行: pip install coursevideogen[llm]"
        )
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    response = client.chat.completions.create(
        model=config.model,
        temperature=config.temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
    )
    return response.choices[0].message.content
