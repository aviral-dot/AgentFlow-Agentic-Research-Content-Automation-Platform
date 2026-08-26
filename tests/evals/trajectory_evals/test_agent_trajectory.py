import asyncio
import uuid

import pytest
from deepeval.integrations.langchain import CallbackHandler
from deepeval.tracing import observe, update_current_trace

from src.graphs.graph import create_graph
from tests.evals.datasets.trajectory_golden import dataset
from tests.evals.metrics.traj_metrics import trajectory_metrics


@observe(type="agent", name="AgentFlow")
async def run_agentflow(
    golden_input: str,
) -> str:
    """Run the real AgentFlow Planner–Executor workflow."""

    thread_id = f"eval-agentflow-{uuid.uuid4()}"

    callback_handler = CallbackHandler(
        name="agentflow-e2e",
        tags=["agentflow", "planner-executor", "e2e"],
    )

    async with create_graph() as graph:
        result = await graph.ainvoke(
            {
                "query": golden_input,
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                },
                "callbacks": [
                    callback_handler,
                ],
            },
        )

    response = result.get("response")

    if response is None:
        response = str(result)

    response = str(response)

    update_current_trace(
        input=golden_input,
        output=response,
    )

    return response


@pytest.mark.asyncio
async def test_agentflow_e2e() -> None:
    """Evaluate the complete AgentFlow Planner–Executor trajectory."""

    for golden in dataset.evals_iterator(
        metrics=trajectory_metrics,
    ):
        task = asyncio.create_task(
            run_agentflow(golden.input)
        )

        dataset.evaluate(task)