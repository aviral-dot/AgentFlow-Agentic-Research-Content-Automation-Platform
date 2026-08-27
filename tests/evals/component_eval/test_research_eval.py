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
from src.nodes.research_node import ResearchNode
from src.states.blogstate import AgentState, Task

from tests.evals.datasets.research_goldens import dataset
from tests.evals.metrics.research_metrics import (
    research_relevancy,
)




def create_research_node() -> ResearchNode:

    gateway = LLMGateway()

    return ResearchNode(
        llm=gateway.get_llm(),
    )





def build_research_state(
    golden,
) -> AgentState:

    task = Task(
        id="research_eval_1",
        type="research",
        description=golden.input,
        depends_on=[],
        use_blog=False,
    )

    state: AgentState = {
        "query": golden.input,
        "request_id": "research-eval",
        "tasks": [task],
        "current_task": task.id,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }

    return state





@observe(
    metrics=[
       research_relevancy,
    ]
)
async def evaluate_research(
    research_node: ResearchNode,
    golden,
) -> dict:

    state = build_research_state(
        golden
    )

    result = await research_node.research(
        state
    )

    

    research = result.get(
        "research"
    )

    if not research:
        raise AssertionError(
            "ResearchNode.research() did not "
            "produce a research artifact."
        )

   

    summary = str(
        research.get(
            "summary",
            "",
        )
    ).strip()

    if not summary:
        raise AssertionError(
            "Research artifact contains an empty summary."
        )

   

    key_findings = research.get(
        "key_findings",
        [],
    )

    if not key_findings:
        raise AssertionError(
            "Research artifact contains no key findings."
        )

    if not isinstance(
        key_findings,
        list,
    ):
        raise AssertionError(
            "Research key_findings must be a list."
        )

   
    findings_text = "\n".join(
        f"- {str(finding).strip()}"
        for finding in key_findings
    )

    actual_output = (
        f"RESEARCH QUERY:\n"
        f"{research.get('query', golden.input)}\n\n"
        f"SUMMARY:\n"
        f"{summary}\n\n"
        f"KEY FINDINGS:\n"
        f"{findings_text}"
    )

    update_current_span(
        test_case=LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
        )
    )

    return research





@pytest.mark.asyncio
@pytest.mark.parametrize(
    "golden",
    dataset.goldens,
)
async def test_research_component(
    golden,
) -> None:

    research_node = create_research_node()

    await evaluate_research(
        research_node=research_node,
        golden=golden,
    )

    assert_test(
        golden=golden,
    )