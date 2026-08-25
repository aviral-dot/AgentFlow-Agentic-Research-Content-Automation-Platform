import pytest


@pytest.fixture
def guardrail_module(monkeypatch):
    monkeypatch.setenv(
        "NVIDIA_API_KEY",
        "test-nvidia-key",
    )

    import importlib

    import src.guardrails.guardrail as guardrail

    return importlib.reload(
        guardrail
    )


def test_extract_safe_decision(
    guardrail_module,
):
    result = {
        "choices": [
            {
                "message": {
                    "content": "safe"
                }
            }
        ]
    }

    assert (
        guardrail_module._extract_safety_decision(
            result
        )
        == "safe"
    )


def test_extract_unsafe_decision(
    guardrail_module,
):
    result = {
        "choices": [
            {
                "message": {
                    "content": "unsafe"
                }
            }
        ]
    }

    assert (
        guardrail_module._extract_safety_decision(
            result
        )
        == "unsafe"
    )


def test_malformed_safety_response_fails_closed(
    guardrail_module,
):
    assert (
        guardrail_module._extract_safety_decision(
            {}
        )
        == "unsafe"
    )


def test_empty_choices_fail_closed(
    guardrail_module,
):
    result = {
        "choices": []
    }

    assert (
        guardrail_module._extract_safety_decision(
            result
        )
        == "unsafe"
    )


@pytest.mark.asyncio
async def test_empty_input_is_rejected(
    guardrail_module,
):
    assert not await (
        guardrail_module.check_input(
            ""
        )
    )

    assert not await (
        guardrail_module.check_input(
            "   "
        )
    )


@pytest.mark.asyncio
async def test_empty_output_is_rejected(
    guardrail_module,
):
    assert not await (
        guardrail_module.check_output(
            ""
        )
    )

    assert not await (
        guardrail_module.check_output(
            "   "
        )
    )


@pytest.mark.asyncio
async def test_input_guardrail_allows_successful_response(
    guardrail_module,
    monkeypatch,
):
    async def fake_generate_async(
        messages
    ):
        return {
            "role": "assistant",
            "content": "allowed",
        }

    monkeypatch.setattr(
        guardrail_module.rails,
        "generate_async",
        fake_generate_async,
    )

    assert await (
        guardrail_module.check_input(
            "Write a blog about AI agents."
        )
    )


@pytest.mark.asyncio
async def test_input_guardrail_blocks_exception_response(
    guardrail_module,
    monkeypatch,
):
    async def fake_generate_async(
        messages
    ):
        return {
            "role": "exception",
            "content": "blocked",
        }

    monkeypatch.setattr(
        guardrail_module.rails,
        "generate_async",
        fake_generate_async,
    )

    assert not await (
        guardrail_module.check_input(
            "test input"
        )
    )


@pytest.mark.asyncio
async def test_input_guardrail_fails_closed_on_exception(
    guardrail_module,
    monkeypatch,
):
    async def fail(
        messages
    ):
        raise RuntimeError(
            "guardrail unavailable"
        )

    monkeypatch.setattr(
        guardrail_module.rails,
        "generate_async",
        fail,
    )

    assert not await (
        guardrail_module.check_input(
            "test input"
        )
    )


@pytest.mark.asyncio
async def test_output_guardrail_allows_safe_content(
    guardrail_module,
    monkeypatch,
):
    async def fake_safety(
        text
    ):
        return {
            "choices": [
                {
                    "message": {
                        "content": "safe"
                    }
                }
            ]
        }

    monkeypatch.setattr(
        guardrail_module,
        "_nvidia_content_safety",
        fake_safety,
    )

    assert await (
        guardrail_module.check_output(
            "A normal technical article."
        )
    )


@pytest.mark.asyncio
async def test_output_guardrail_blocks_unsafe_content(
    guardrail_module,
    monkeypatch,
):
    async def fake_safety(
        text
    ):
        return {
            "choices": [
                {
                    "message": {
                        "content": "unsafe"
                    }
                }
            ]
        }

    monkeypatch.setattr(
        guardrail_module,
        "_nvidia_content_safety",
        fake_safety,
    )

    assert not await (
        guardrail_module.check_output(
            "unsafe content"
        )
    )


@pytest.mark.asyncio
async def test_output_guardrail_fails_closed_on_error(
    guardrail_module,
    monkeypatch,
):
    async def fail(
        text
    ):
        raise RuntimeError(
            "NVIDIA unavailable"
        )

    monkeypatch.setattr(
        guardrail_module,
        "_nvidia_content_safety",
        fail,
    )

    assert not await (
        guardrail_module.check_output(
            "test output"
        )
    )