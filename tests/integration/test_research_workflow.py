import pytest

from src.executors.workflow_executor import WorkflowExecutor
from src.nodes import research_node
from src.nodes.research_node import ResearchNode
from src.states.blogstate import Task


class FakeResearchTool:
    async def search(
        self,
        query,
        max_results,
    ):
        return {
            "sources": [
                {
                    "title": "AI Agents",
                    "content": (
                        "AI agents can plan and "
                        "execute multi-step tasks."
                    ),
                    "score": 0.95,
                }
            ]
        }


class FakeStructuredLLM:
    async def ainvoke(
        self,
        prompt,
    ):
        return type(
            "Result",
            (),
            {
                "summary": (
                    "AI agents can plan and "
                    "execute multi-step tasks."
                ),
                "key_findings": [
                    "Agents can plan tasks.",
                    "Agents can execute tasks.",
                ],
            },
        )()


class FakeLLM:
    def with_structured_output(
        self,
        schema,
    ):
        return FakeStructuredLLM()


@pytest.mark.asyncio
async def test_research_worker_completes_executor_task(
    monkeypatch,
):
    monkeypatch.setattr(
        research_node,
        "ResearchTool",
        FakeResearchTool,
    )

    task = Task(
        id="task_1",
        type="research",
        description="Research AI agents",
        status="running",
    )

    state = {
        "tasks": [task],
        "current_task": "task_1",
        "completed_tasks": [],
        "running_tasks": ["task_1"],
        "task_results": {},
    }

    node = ResearchNode(
        FakeLLM()
    )

    result = await node.research(
        state
    )

    state.update(result)

    executor = WorkflowExecutor()

    updates = executor.mark_task_completed(
        state,
        "task_1",
        result["task_result"],
    )

    state.update(updates)

    assert (
        state["tasks"][0].status
        == "completed"
    )

    assert (
        state["completed_tasks"]
        == ["task_1"]
    )

    assert (
        state["task_results"]["task_1"]
        == result["task_result"]
    )