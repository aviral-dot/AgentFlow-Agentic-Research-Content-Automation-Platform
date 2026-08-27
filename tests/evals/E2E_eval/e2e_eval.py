import uuid

import pytest
from deepeval import assert_test
from deepeval.integrations.langchain import CallbackHandler
from deepeval.tracing import observe, update_current_trace

from src.graphs.graph import create_graph
from tests.evals.datasets.E2E_goldens import dataset
from tests.evals.metrics.E2E_metrics import agent_e2e_metrics


@observe()
async def run_agentflow(golden_input: str) -> str:
    """Run the complete AgentFlow Planner–Executor workflow."""

    thread_id = f"eval-e2e-{uuid.uuid4()}"

    callback_handler = CallbackHandler(
        name="agentflow-e2e",
        tags=["agentflow", "planner-executor", "e2e"],
    )

    async with create_graph() as graph:
        result = await graph.ainvoke(
            {"query": golden_input},
            config={
                "configurable": {"thread_id": thread_id},
                "callbacks": [callback_handler],
            },
        )

    response = result.get("response")
    if response is None:
        response = str(result)
    response = str(response)

    update_current_trace(input=golden_input, output=response)

    return response


@pytest.mark.asyncio
@pytest.mark.parametrize("golden", dataset.goldens)
async def test_agentflow_e2e(golden) -> None:
    """Evaluate the complete AgentFlow end-to-end."""

    await run_agentflow(golden.input)
    assert_test(golden=golden, metrics=agent_e2e_metrics)