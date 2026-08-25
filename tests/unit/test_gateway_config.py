def test_gateway_config_defaults():
    from src.gateway.config import (
        LLMGatewayConfig,
    )

    assert (
        LLMGatewayConfig.PRIMARY_MODEL
    )

    assert (
        LLMGatewayConfig.FALLBACK_MODEL
    )

    assert (
        LLMGatewayConfig.ROUTING_STRATEGY
    )

    assert (
        LLMGatewayConfig.NUM_RETRIES
        >= 0
    )

    assert (
        LLMGatewayConfig.TIMEOUT
        > 0
    )

    assert (
        LLMGatewayConfig.CACHE_TTL
        > 0
    )


def test_gateway_config_validation_requires_groq_key(
    monkeypatch,
):
    from src.gateway.config import (
        LLMGatewayConfig,
    )

    monkeypatch.delenv(
        "GROQ_API_KEY",
        raising=False,
    )

    try:
        LLMGatewayConfig.validate()
    except RuntimeError as exc:
        assert (
            "GROQ_API_KEY"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected RuntimeError"
        )


def test_gateway_config_validation_accepts_groq_key(
    monkeypatch,
):
    from src.gateway.config import (
        LLMGatewayConfig,
    )

    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    LLMGatewayConfig.validate()