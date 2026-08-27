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
from src.nodes.mail_node import EmailNode
from src.states.blogstate import AgentState, Task

from tests.evals.datasets.email_goldens import dataset
from tests.evals.helpers.formatting import format_email
from tests.evals.metrics.email_metrics import email_quality





def create_email_node() -> EmailNode:

    gateway = LLMGateway()

    return EmailNode(
        llm=gateway.get_llm(),
    )





def build_email_state(
    golden,
) -> AgentState:
    """
    Build the minimal AgentState required by EmailNode.

    This is an isolated EmailNode component evaluation.

    No BlogNode is executed.
    No Blog artifact is provided.
    No blog dependency exists.

    EmailNode therefore uses its normal
    non-blog email generation path.
    """

    task = Task(
        id="email_eval_1",
        type="email",
        description=golden.input,
        depends_on=[],
        use_blog=False,
    )

    state: AgentState = {
        "query": golden.input,
        "request_id": "email-eval",
        "tasks": [task],
        "current_task": task.id,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }

    return state





@observe(
    metrics=[
        email_quality,
    ]
)
async def evaluate_email(
    email_node: EmailNode,
    golden,
) -> str:
    """
    Evaluate EmailNode as an isolated component.

    Flow:

        Golden
          ↓
        AgentState
          ↓
        EmailNode.draft_email()
          ↓
        Email
          ↓
        DeepEval
          ↓
        email_quality
    """

    state = build_email_state(
        golden
    )

    result = await email_node.draft_email(
        state
    )

  
    email = result.get(
        "email"
    )

    if not email:

        raise AssertionError(
            "EmailNode.draft_email() did not "
            "produce an email."
        )

  
    output = format_email(
        email
    )

    if not output.strip():

        raise AssertionError(
            "Generated email output is empty."
        )

   

    update_current_span(
        test_case=LLMTestCase(
            input=golden.input,
            actual_output=output,
        )
    )

    return output





@pytest.mark.asyncio
@pytest.mark.parametrize(
    "golden",
    dataset.goldens,
)
async def test_email_component(
    golden,
) -> None:

    email_node = create_email_node()

    await evaluate_email(
        email_node=email_node,
        golden=golden,
    )

    assert_test(
        golden=golden,
    )