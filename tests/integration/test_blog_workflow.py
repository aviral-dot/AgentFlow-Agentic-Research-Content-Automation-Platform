import pytest

from src.nodes.blog_node import BlogNode
from src.states.blogstate import Task


class FakeResponse:
    def __init__(
        self,
        content,
    ):
        self.content = content


class FakeLLM:
    def __init__(self):
        self.calls = []

    async def ainvoke(
        self,
        prompt,
    ):
        self.calls.append(prompt)

        if "Return ONLY the title" in prompt:
            return FakeResponse(
                "AI Agents in Modern Software"
            )

        return FakeResponse(
            "# AI Agents\n\n"
            "AI agents can coordinate "
            "multi-step tasks."
        )


@pytest.mark.asyncio
async def test_blog_workflow_generates_title_then_content():
    task = Task(
        id="task_blog",
        type="blog",
        description="Write a blog about AI agents",
        status="running",
    )

    state = {
        "query": "Write a blog about AI agents",
        "tasks": [task],
        "current_task": "task_blog",
        "research": {
            "topic": "AI agents",
            "summary": (
                "AI agents coordinate tasks."
            ),
            "key_points": [
                "Planning",
                "Tool usage",
            ],
            "sources": [],
        },
        "blog": None,
    }

    llm = FakeLLM()

    node = BlogNode(llm)

    title_result = (
        await node.title_creation(
            state
        )
    )

    state.update(
        title_result
    )

    assert (
        state["blog"]["title"]
        == "AI Agents in Modern Software"
    )

    content_result = (
        await node.content_generation(
            state
        )
    )

    state.update(
        content_result
    )

    assert (
        state["blog"]["title"]
        == "AI Agents in Modern Software"
    )

    assert (
        "AI agents"
        in state["blog"]["content"]
    )

    assert (
        state["task_result"]
        == state["blog"]
    )