import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from tests.evals.datasets.planner_goldens import dataset
from evals.helpers.formatting import format_plan
from tests.unit.helpers.plan_assertions import (
    assert_acyclic,
    assert_valid_plan,
)
from evals.metrics.planner_metrics import plan_quality

from src.gateway.llm_gateway import LLMGateway
from src.planners.workflow_planner import WorkflowPlanner


@pytest.fixture(scope="module")
def planner():

    gateway = LLMGateway()

    return WorkflowPlanner(
        llm=gateway.get_llm()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("golden", dataset.goldens)
async def test_planner_quality(
    planner,
    golden,
):

    result = await planner.plan(
        {
            "query": golden.input,
        }
    )

    tasks = result["tasks"]

    assert_valid_plan(tasks)
    assert_acyclic(tasks)

    actual_plan = format_plan(tasks)

    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_plan,
    )

    assert_test(
        test_case=test_case,
        metrics=[
            plan_quality,
        ],
    )

