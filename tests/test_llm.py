import pytest
from unittest.mock import patch, MagicMock
from core.llm import LLMConfig, resolve_llm_config, extract_json, call_llm

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
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "env-key",
        "OPENAI_BASE_URL": "https://env.base.url",
        "CVG_MODEL": "env-model"
    }):
        config = resolve_llm_config(
            api_key="cli-key",
            base_url="https://cli.base.url",
            model="cli-model",
            temperature=0.9
        )
        assert config.api_key == "cli-key"
        assert config.base_url == "https://cli.base.url"
        assert config.model == "cli-model"
        assert config.temperature == 0.9

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

def test_call_llm_success():
    config = LLMConfig(api_key="test-key", base_url="https://api.test.com", model="test-model", temperature=0.7)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="LLM response text"))]

    with patch("core.llm.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response

        result = call_llm("system prompt", "user text", config)

        assert result == "LLM response text"
        MockOpenAI.assert_called_once_with(api_key="test-key", base_url="https://api.test.com")
        mock_client.chat.completions.create.assert_called_once()

def test_call_llm_import_error():
    config = LLMConfig(api_key="test", base_url="x", model="y", temperature=0.7)

    with patch("core.llm.OpenAI", side_effect=ImportError("No module named 'openai'")):
        with pytest.raises(ImportError, match="pip install coursevideogen\\[llm\\]"):
            call_llm("system", "user", config)
