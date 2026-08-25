from types import SimpleNamespace

import pytest

from src.nodes.blog_node import BlogNode
from src.states.blogstate import Task


class FakeLLM:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    async def ainvoke(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(
            content=next(self.responses)
        )


def make_state(
    description="Write a blog about AI agents",
    research=None,
):
    task = Task(
        id="task_1",
        type="blog",
        description=description,
        depends_on=[],
        use_blog=False,
        status="running",
    )

    return {
        "query": description,
        "tasks": [task],
        "current_task": "task_1",
        "blog": None,
        "research": research,
    }


@pytest.mark.asyncio
async def test_title_creation_returns_blog_title():
    llm = FakeLLM(
        ["The Future of AI Agents"]
    )

    node = BlogNode(llm)

    result = await node.title_creation(
        make_state()
    )

    assert result == {
        "blog": {
            "title": "The Future of AI Agents"
        }
    }


@pytest.mark.asyncio
async def test_title_creation_uses_research_context():
    llm = FakeLLM(
        ["AI Agents in Modern Software"]
    )

    node = BlogNode(llm)

    state = make_state(
        research={
            "topic": "AI agents",
            "summary": "Agents automate multi-step workflows.",
            "key_points": [
                "Agents use tools.",
                "Agents plan tasks.",
            ],
            "sources": [
                "https://example.com"
            ],
        }
    )

    result = await node.title_creation(
        state
    )

    assert result["blog"]["title"] == (
        "AI Agents in Modern Software"
    )

    assert "Agents automate" in llm.prompts[0]
    assert "Agents use tools." in llm.prompts[0]


@pytest.mark.asyncio
async def test_title_creation_rejects_missing_description():
    llm = FakeLLM(
        ["unused"]
    )

    node = BlogNode(llm)

    state = make_state(
        description="   "
    )

    state["query"] = None

    with pytest.raises(
        ValueError,
        match="Blog description is missing",
    ):
        await node.title_creation(
            state
        )


@pytest.mark.asyncio
async def test_content_generation_requires_title():
    llm = FakeLLM(
        ["unused"]
    )

    node = BlogNode(llm)

    state = make_state()

    state["blog"] = {}

    with pytest.raises(
        ValueError,
        match="Blog title is missing",
    ):
        await node.content_generation(
            state
        )


@pytest.mark.asyncio
async def test_content_generation_returns_blog():
    llm = FakeLLM(
        [
            "AI Agents: An Introduction"
        ]
    )

    node = BlogNode(llm)

    state = make_state()

    state["blog"] = {
        "title": "AI Agents"
    }

    result = await node.content_generation(
        state
    )

    assert result["blog"]["title"] == "AI Agents"
    assert (
        result["blog"]["content"]
        == "AI Agents: An Introduction"
    )
    assert (
        result["task_result"]
        == result["blog"]
    )


def test_blog_description_prefers_current_task():
    node = BlogNode(
        FakeLLM(["unused"])
    )

    state = make_state(
        description="Task description"
    )

    state["query"] = "Original query"

    assert (
        node._get_blog_description(
            state
        )
        == "Task description"
    )


def test_blog_description_falls_back_to_query():
    node = BlogNode(
        FakeLLM(["unused"])
    )

    state = {
        "current_task": None,
        "tasks": [],
        "query": "Original query",
    }

    assert (
        node._get_blog_description(
            state
        )
        == "Original query"
    )


def test_research_context_is_empty_without_research():
    node = BlogNode(
        FakeLLM(["unused"])
    )

    assert (
        node._get_research_context(
            {"research": None}
        )
        == ""
    )


def test_research_context_formats_research():
    node = BlogNode(
        FakeLLM(["unused"])
    )

    state = {
        "research": {
            "topic": "AI",
            "summary": "AI summary",
            "key_points": [
                "Point one",
                "Point two",
            ],
            "sources": [
                "source-url"
            ],
        }
    }

    context = node._get_research_context(
        state
    )

    assert "Research Topic:" in context
    assert "AI" in context
    assert "AI summary" in context
    assert "Point one" in context
    assert "source-url" in context