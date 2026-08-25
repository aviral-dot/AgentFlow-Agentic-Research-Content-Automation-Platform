from src.gateway import llm_gateway


class FakeRouter:
    def __init__(
        self,
        **kwargs,
    ):
        self.kwargs = kwargs


class FakeChatLiteLLMRouter:
    def __init__(
        self,
        **kwargs,
    ):
        self.kwargs = kwargs


def test_get_api_key_for_groq(
    monkeypatch,
):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "groq-test",
    )

    assert (
        llm_gateway.LLMGateway._get_api_key(
            "groq/openai/gpt-oss-20b"
        )
        == "groq-test"
    )


def test_get_api_key_for_gemini(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "gemini-test",
    )

    assert (
        llm_gateway.LLMGateway._get_api_key(
            "gemini/gemini-3.7-flash"
        )
        == "gemini-test"
    )


def test_get_api_key_for_unknown_provider():
    assert (
        llm_gateway.LLMGateway._get_api_key(
            "unknown/model"
        )
        is None
    )


def test_fallback_available_when_gemini_key_exists(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test",
    )

    assert (
        llm_gateway.LLMGateway._fallback_available()
    )


def test_fallback_unavailable_without_gemini_key(
    monkeypatch,
):
    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    assert not (
        llm_gateway.LLMGateway._fallback_available()
    )


def test_gateway_builds_primary_and_fallback(
    monkeypatch,
):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "groq-test",
    )
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "gemini-test",
    )

    monkeypatch.setattr(
        llm_gateway,
        "Router",
        FakeRouter,
    )

    gateway = llm_gateway.LLMGateway()

    assert len(
        gateway.model_list
    ) == 2

    assert (
        gateway.model_list[0]["model_name"]
        == "primary"
    )

    assert (
        gateway.model_list[1]["model_name"]
        == "fallback"
    )

    assert (
        gateway.router.kwargs[
            "fallbacks"
        ]
        == [
            {
                "primary": [
                    "fallback"
                ]
            }
        ]
    )


def test_gateway_caches_llm_clients(
    monkeypatch,
):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "groq-test",
    )

    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    monkeypatch.setattr(
        llm_gateway,
        "Router",
        FakeRouter,
    )

    monkeypatch.setattr(
        llm_gateway,
        "ChatLiteLLMRouter",
        FakeChatLiteLLMRouter,
    )

    gateway = llm_gateway.LLMGateway()

    first = gateway.get_llm(
        "primary",
        temperature=0.2,
    )

    second = gateway.get_llm(
        "primary",
        temperature=0.2,
    )

    assert first is second

    assert len(
        gateway._models
    ) == 1


def test_gateway_creates_separate_clients_for_temperature(
    monkeypatch,
):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "groq-test",
    )

    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    monkeypatch.setattr(
        llm_gateway,
        "Router",
        FakeRouter,
    )

    monkeypatch.setattr(
        llm_gateway,
        "ChatLiteLLMRouter",
        FakeChatLiteLLMRouter,
    )

    gateway = llm_gateway.LLMGateway()

    first = gateway.get_llm(
        "primary",
        temperature=0.1,
    )

    second = gateway.get_llm(
        "primary",
        temperature=0.7,
    )

    assert first is not second

    assert len(
        gateway._models
    ) == 2