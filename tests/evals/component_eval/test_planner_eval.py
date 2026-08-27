# mypy: ignore-errors

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.tracing import observe, update_current_span

from src.gateway.llm_gateway import LLMGateway
from src.planners.workflow_planner import WorkflowPlanner

from tests.evals.datasets.planner_goldens import dataset
from tests.evals.metrics.planner_metrics import planner_quality




def create_workflow_planner() -> WorkflowPlanner:

    gateway = LLMGateway()

    return WorkflowPlanner(
        llm=gateway.get_llm(),
    )





def build_planner_state(
    golden,
):

    return {
        "query": golden.input,
        "request_id": "planner-eval",
        "tasks": [],
        "current_task": None,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }





@observe(
    metrics=[
        planner_quality,
    ]
)
async def evaluate_planner(
    planner: WorkflowPlanner,
    golden,
):

    state = build_planner_state(
        golden
    )

    result = await planner.plan(
        state
    )

    tasks = result.get(
        "tasks"
    )

    if not tasks:
        raise AssertionError(
            "WorkflowPlanner.plan() did not produce tasks."
        )

    
    task_ids = [
        task.id
        for task in tasks
    ]

    if len(task_ids) != len(set(task_ids)):
        raise AssertionError(
            "Planner produced duplicate task IDs."
        )

   

    task_lines = []

    for task in tasks:

        task_lines.append(
            (
                f"TASK ID: {task.id}\n"
                f"TYPE: {task.type}\n"
                f"DESCRIPTION: {task.description}\n"
                f"DEPENDS_ON: {task.depends_on}\n"
                f"USE_BLOG: {task.use_blog}\n"
            )
        )

    actual_output = "\n".join(
        task_lines
    )

   

    print("=== ACTUAL OUTPUT ===")
    print(actual_output)
    print("======================")


    update_current_span(
        test_case=LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
        )
    )

    return tasks





@pytest.mark.asyncio
@pytest.mark.parametrize(
    "golden",
    dataset.goldens,
)
async def test_planner_component(
    golden,
) -> None:

    planner = create_workflow_planner()

    await evaluate_planner(
        planner=planner,
        golden=golden,
    )

    assert_test(
        golden=golden,
    )

