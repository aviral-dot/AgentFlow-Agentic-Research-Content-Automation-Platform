import uuid

import pytest
from deepeval.evaluate import AsyncConfig
from deepeval.integrations.langchain import CallbackHandler

from src.graphs.graph import create_graph
from tests.evals.datasets.E2E_goldens import dataset
from tests.evals.metrics.E2E_metrics import agent_e2e_metrics


async def run_agentflow(
    golden_input: str,
) -> None:
    """Run the complete AgentFlow Planner–Executor workflow."""

    thread_id = f"eval-e2e-{uuid.uuid4()}"

    callback_handler = CallbackHandler(
        name="agentflow-e2e",
        tags=[
            "agentflow",
            "planner-executor",
            "e2e",
        ],
    )

    async with create_graph() as graph:

        await graph.ainvoke(
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


@pytest.mark.asyncio
async def test_agentflow_e2e() -> None:
    """Evaluate the complete AgentFlow end-to-end."""

    for golden in dataset.evals_iterator(
        metrics=agent_e2e_metrics,
        async_config=AsyncConfig(
            run_async=False
        ),
    ):
        await run_agentflow(
            golden.input
        )