import pytest
from unittest.mock import patch, MagicMock
from core.llm import LLMConfig, resolve_llm_config, extract_json

def test_llm_config_frozen():
    config = LLMConfig(api_key="x", base_url="y", model="z", temperature=0.7)
    with pytest.raises(Exception):  # frozen dataclass
        config.api_key = "new"

def test_resolve_llm_config_defaults():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        config = resolve_llm_config()
        assert config.api_key == "test-key"
        assert config.base_url == "https://open.bigmodel.cn/api/paas/v4"
        assert config.model == "glm-4-flash"
        assert config.temperature == 0.7

def test_resolve_llm_config_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            resolve_llm_config()

def test_resolve_llm_config_cli_overrides_env():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key", "CVG_MODEL": "env-model"}):
        config = resolve_llm_config(api_key="cli-key", model="cli-model")
        assert config.api_key == "cli-key"
        assert config.model == "cli-model"
        assert config.base_url == "https://open.bigmodel.cn/api/paas/v4"

def test_extract_json_from_fenced_block():
    text = '```json\n{"key": "value"}\n```'
    assert extract_json(text) == {"key": "value"}

def test_extract_json_from_plain():
    assert extract_json('{"key": "value"}') == {"key": "value"}

def test_extract_json_with_extra_text():
    text = '以下是 JSON：\n{"key": "value"}\n以上'
    assert extract_json(text) == {"key": "value"}

def test_extract_json_invalid_raises():
    with pytest.raises(ValueError):
        extract_json("not json at all")
