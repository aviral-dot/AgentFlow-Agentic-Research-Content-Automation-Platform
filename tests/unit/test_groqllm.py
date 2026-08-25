import pytest

from src.llms.groqllm import GroqLLM


def test_groq_llm_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "GROQ_API_KEY",
        raising=False,
    )

    monkeypatch.setattr(
        "src.llms.groqllm.load_dotenv",
        lambda: None,
    )

    llm_factory = GroqLLM()

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is not configured",
    ):
        llm_factory.get_llm()


def test_groq_llm_creates_chatgroq(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-groq-api-key",
    )

    llm_factory = GroqLLM()

    llm = llm_factory.get_llm()

    assert llm is not None
    assert llm_factory.groq_api_key == "test-groq-api-key"


def test_groq_llm_wraps_unexpected_error(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-groq-api-key",
    )

    llm_factory = GroqLLM()

    def raise_unexpected_error(*args, **kwargs):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(
        "src.llms.groqllm.ChatGroq",
        raise_unexpected_error,
    )

    with pytest.raises(
        ValueError,
        match="Failed to initialize Groq LLM",
    ):
        llm_factory.get_llm()