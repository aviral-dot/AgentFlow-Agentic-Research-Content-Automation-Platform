import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.integrations.langchain import CallbackHandler

from tests.evals.datasets.agentflow_goldens import dataset
from tests.evals.metrics.agent_metrics import (
    plan_adherence_metric,
    plan_quality_metric,
    step_efficiency_metric,
    task_completion_metric,
)
from src.graphs.graph import create_graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "golden",
    dataset.goldens,
)
async def test_agentflow_e2e(golden):

    callback_handler = CallbackHandler(
        name="agentflow-e2e",
        tags=["agentflow", "e2e"],
        thread_id=f"eval-{golden.input}",
    )

    async with create_graph() as graph:

        result = await graph.ainvoke(
            {
                "query": golden.input,
            },
            config={
                "configurable": {
                    "thread_id": f"eval-{golden.input}",
                },
                "callbacks": [
                    callback_handler,
                ],
            },
        )

    actual_output = str(result)

    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_output,
    )

    assert_test(
        test_case=test_case,
        metrics=[
            task_completion_metric,
            step_efficiency_metric,
            plan_quality_metric,
            plan_adherence_metric,
        ],
    )