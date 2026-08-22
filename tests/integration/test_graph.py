from types import SimpleNamespace

import pytest

from src.graphs.graph_builder import GraphBuilder
from src.nodes.supervisor_node import SupervisorDecision


class FakeStructuredLLM:

    def __init__(self, route):
        self.route = route

    async def ainvoke(self, prompt):
        return SupervisorDecision(
            route=self.route
        )


class FakeLLM:

    def __init__(self, route):
        self.route = route

    def with_structured_output(
        self,
        schema,
        **kwargs,
    ):
        return FakeStructuredLLM(self.route)

    async def ainvoke(self, prompt):
        if "title" in prompt.lower():
            return SimpleNamespace(
                content="Generative AI: The Future"
            )

        return SimpleNamespace(
            content="Generative AI is changing technology."
        )


@pytest.mark.asyncio
async def test_blog_graph_completes():
    llm = FakeLLM("blog")

    builder = GraphBuilder(llm)
    graph = builder.setup_graph()

    result = await graph.ainvoke(
        {
            "query": "Write a blog about Generative AI"
        }
    )

    assert result["route"] == "blog"

    assert result["blog"]["title"] == (
        "Generative AI: The Future"
    )

    assert result["blog"]["content"] == (
        "Generative AI is changing technology."
    )