import pytest

from deepeval import assert_test
from deepeval.integrations.langchain import CallbackHandler

from evals.agent.dataset import dataset
from evals.agent.metrics import (
    task_completion_metric,
    step_efficiency_metric,
)
from src.graphs.graph import graph


@pytest.mark.asyncio
@pytest.mark.parametrize("golden", dataset.goldens)
async def test_agent_workflow(golden):

    callback_handler = CallbackHandler()

    await graph.ainvoke(
        {
            "query": golden.input,
        },
        config={
            "callbacks": [
                callback_handler,
            ],
        },
    )

    assert_test(
        golden=golden,
        metrics=[
            task_completion_metric,
            step_efficiency_metric,
        ],
    )