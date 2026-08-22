from unittest.mock import patch

from src.gateway.llm_gateway import LLMGateway


def test_get_api_key_returns_groq_key():
    with patch.dict(
        "os.environ",
        {"GROQ_API_KEY": "groq-test-key"},
        clear=True,
    ):
        result = LLMGateway._get_api_key(
            "groq/test-model"
        )

    assert result == "groq-test-key"


def test_get_api_key_returns_gemini_key():
    with patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": "gemini-test-key"},
        clear=True,
    ):
        result = LLMGateway._get_api_key(
            "gemini/test-model"
        )

    assert result == "gemini-test-key"


def test_get_api_key_returns_none_for_unknown_provider():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        result = LLMGateway._get_api_key(
            "unknown/test-model"
        )

    assert result is None


def test_get_api_key_returns_none_when_groq_key_missing():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        result = LLMGateway._get_api_key(
            "groq/test-model"
        )

    assert result is None


def test_fallback_available_when_gemini_key_exists():
    with patch.dict(
        "os.environ",
        {
            "GEMINI_API_KEY": "test-key"
        },
        clear=True,
    ):
        assert LLMGateway._fallback_available() is True


def test_fallback_unavailable_without_gemini_key():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        assert LLMGateway._fallback_available() is False