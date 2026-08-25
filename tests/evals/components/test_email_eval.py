import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from tests.evals.datasets.email_goldens import EMAIL_REQUESTS
from evals.helpers.formatting import format_email
from evals.metrics.email_metrics import email_quality

from src.gateway.llm_gateway import LLMGateway
from src.nodes.mail_node import EmailNode
from src.states.blogstate import AgentState, Task


@pytest.fixture(scope="module")
def email_node():

    gateway = LLMGateway()

    return EmailNode(
        llm=gateway.get_llm(),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    EMAIL_REQUESTS,
)
async def test_email_component(
    email_node,
    query,
):

    task = Task(
        id="email_eval_1",
        type="email",
        description=query,
        depends_on=[],
        use_blog=False,
    )

    state: AgentState = {
        "query": query,
        "request_id": "email-eval",
        "tasks": [task],
        "current_task": task.id,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }

    result = await email_node.draft_email(
        state
    )

    email = result.get("email")

    output = format_email(email)

    assert output.strip()

    test_case = LLMTestCase(
        input=query,
        actual_output=output,
    )

    assert_test(
        test_case=test_case,
        metrics=[
            email_quality,
        ],
    )