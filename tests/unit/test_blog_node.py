from types import SimpleNamespace

import pytest

from src.nodes.blog_node import BlogNode


@pytest.mark.asyncio
async def test_title_creation_returns_title():
    async def fake_ainvoke(prompt):
        return SimpleNamespace(
            content="The Future of Generative AI"
        )

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    state = {
        "query": "Generative AI"
    }

    result = await node.title_creation(state)

    assert result["blog"]["title"] == (
        "The Future of Generative AI"
    )


@pytest.mark.asyncio
async def test_title_creation_passes_query_to_llm():
    captured_prompt = None

    async def fake_ainvoke(prompt):
        nonlocal captured_prompt

        captured_prompt = prompt

        return SimpleNamespace(
            content="The Future of Generative AI"
        )

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    state = {
        "query": "Generative AI"
    }

    await node.title_creation(state)

    assert captured_prompt is not None
    assert "Generative AI" in captured_prompt


@pytest.mark.asyncio
async def test_content_generation_uses_existing_title():
    async def fake_ainvoke(prompt):
        return SimpleNamespace(
            content=(
                "Generative AI is transforming "
                "software development."
            )
        )

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    state = {
        "query": "Generative AI",
        "blog": {
            "title": "The Future of Generative AI"
        },
    }

    result = await node.content_generation(state)

    assert result["blog"]["title"] == (
        "The Future of Generative AI"
    )

    assert result["blog"]["content"] == (
        "Generative AI is transforming "
        "software development."
    )


@pytest.mark.asyncio
async def test_content_generation_passes_title_to_llm():
    captured_prompt = None

    async def fake_ainvoke(prompt):
        nonlocal captured_prompt

        captured_prompt = prompt

        return SimpleNamespace(
            content="Generated blog content."
        )

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    state = {
        "query": "Generative AI",
        "blog": {
            "title": "The Future of Generative AI"
        },
    }

    await node.content_generation(state)

    assert captured_prompt is not None
    assert "The Future of Generative AI" in captured_prompt


@pytest.mark.asyncio
async def test_title_creation_does_not_call_llm_for_empty_query():
    called = False

    async def fake_ainvoke(prompt):
        nonlocal called

        called = True

        return SimpleNamespace(
            content="title"
        )

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    result = await node.title_creation({
        "query": ""
    })

    assert result == {}
    assert called is False


@pytest.mark.asyncio
async def test_title_creation_propagates_llm_failure():
    async def fake_ainvoke(prompt):
        raise RuntimeError("LLM unavailable")

    llm = SimpleNamespace(
        ainvoke=fake_ainvoke
    )

    node = BlogNode(llm)

    state = {
        "query": "Generative AI"
    }

    with pytest.raises(RuntimeError, match="LLM unavailable"):
        await node.title_creation(state)