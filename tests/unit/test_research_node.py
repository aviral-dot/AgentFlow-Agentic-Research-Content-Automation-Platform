from types import SimpleNamespace

import pytest

from src.nodes import research_node
from src.nodes.research_node import ResearchNode
from src.states.blogstate import Task


class FakeStructuredLLM:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.prompts = []

    async def ainvoke(self, prompt):
        self.prompts.append(prompt)

        if self.error:
            raise self.error

        return self.result


class FakeLLM:
    def __init__(self, structured_result=None):
        self.structured = FakeStructuredLLM(
            result=structured_result
        )

    def with_structured_output(self, schema):
        return self.structured


class FakeResearchTool:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    async def search(self, **kwargs):
        self.calls.append(kwargs)

        if self.error:
            raise self.error

        return self.result


def make_state(
    task_type="research",
    description="Research AI agents",
):
    task = Task(
        id="task_1",
        type=task_type,
        description=description,
        depends_on=[],
        use_blog=False,
        status="running",
    )

    return {
        "request_id": "req-1",
        "query": description,
        "tasks": [task],
        "current_task": "task_1",
        "completed_tasks": [],
        "running_tasks": ["task_1"],
        "task_results": {},
    }


@pytest.mark.asyncio
async def test_research_node_returns_compact_research_result(
    monkeypatch,
):
    fake_tool = FakeResearchTool(
        result={
            "sources": [
                {
                    "title": "Low Score",
                    "content": "low score content",
                    "score": 0.2,
                },
                {
                    "title": "High Score",
                    "content": "high score content",
                    "score": 0.9,
                },
            ]
        }
    )

    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: fake_tool,
    )

    llm = FakeLLM(
        structured_result=SimpleNamespace(
            summary="AI agents coordinate tasks.",
            key_findings=[
                "Agents can delegate work.",
                "Agents can use tools.",
            ],
        )
    )

    node = ResearchNode(llm)

    result = await node.research(
        make_state()
    )

    assert result["research"]["query"] == "Research AI agents"
    assert (
        result["research"]["summary"]
        == "AI agents coordinate tasks."
    )

    assert result["research"]["key_findings"] == [
        "Agents can delegate work.",
        "Agents can use tools.",
    ]

    assert result["task_result"] == result["research"]

    assert fake_tool.calls == [
        {
            "query": "Research AI agents",
            "max_results": 5,
        }
    ]

    assert "high score content" in llm.structured.prompts[0]


@pytest.mark.asyncio
async def test_research_node_rejects_missing_current_task(
    monkeypatch,
):
    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: FakeResearchTool(),
    )

    node = ResearchNode(
        FakeLLM()
    )

    state = {
        "tasks": [],
        "current_task": None,
    }

    with pytest.raises(
        ValueError,
        match="No current research task exists",
    ):
        await node.research(state)


@pytest.mark.asyncio
async def test_research_node_rejects_non_research_task(
    monkeypatch,
):
    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: FakeResearchTool(),
    )

    node = ResearchNode(
        FakeLLM()
    )

    state = make_state(
        task_type="blog"
    )

    with pytest.raises(
        ValueError,
        match="not a research task",
    ):
        await node.research(state)


@pytest.mark.asyncio
async def test_research_node_rejects_empty_description(
    monkeypatch,
):
    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: FakeResearchTool(),
    )

    node = ResearchNode(
        FakeLLM()
    )

    state = make_state(
        description="   "
    )

    with pytest.raises(
        ValueError,
        match="description cannot be empty",
    ):
        await node.research(state)


@pytest.mark.asyncio
async def test_research_node_rejects_no_sources(
    monkeypatch,
):
    fake_tool = FakeResearchTool(
        result={
            "sources": []
        }
    )

    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: fake_tool,
    )

    node = ResearchNode(
        FakeLLM()
    )

    with pytest.raises(
        ValueError,
        match="returned no sources",
    ):
        await node.research(
            make_state()
        )


@pytest.mark.asyncio
async def test_research_node_rejects_unusable_source_content(
    monkeypatch,
):
    fake_tool = FakeResearchTool(
        result={
            "sources": [
                {
                    "title": "No content",
                    "content": "",
                    "score": 1.0,
                }
            ]
        }
    )

    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        lambda: fake_tool,
    )

    node = ResearchNode(
        FakeLLM()
    )

    with pytest.raises(
        ValueError,
        match="No usable research content",
    ):
        await node.research(
            make_state()
        )


def test_research_node_normalizes_findings():
    result = ResearchNode._normalize_findings(
        [
            " First finding ",
            "",
            "First finding",
            "Second finding",
            "Third finding",
            "Fourth finding",
        ]
    )

    assert result == [
        "First finding",
        "Second finding",
        "Third finding",
    ]


def test_research_node_builds_context_with_content_limit():
    source = {
        "title": "Example",
        "content": "x" * 2000,
    }

    context = ResearchNode._build_llm_context(
        [source]
    )

    assert "SOURCE 1" in context
    assert "Example" in context
    assert len(context.split("Example\n", 1)[1]) == 1000