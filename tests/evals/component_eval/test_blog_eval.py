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
from src.nodes.blog_node import BlogNode
from src.states.blogstate import AgentState, Blog, Task

from tests.evals.datasets.blog_goldens import dataset
from tests.evals.metrics.blog_metrics import (
    blog_content_metric,
)





def create_blog_node() -> BlogNode:
    gateway = LLMGateway()

    return BlogNode(
        llm=gateway.get_llm(),
    )





def build_blog_state(
    golden,
) -> AgentState:
    """
    Build the minimal AgentState required by BlogNode.

    This is an isolated BlogNode component evaluation.

    The test intentionally does NOT provide a research
    artifact. Therefore BlogNode will execute its normal
    no-research prompt path.
    """

    query = golden.input

    task = Task(
        id="blog_eval_1",
        type="blog",
        description=query,
        depends_on=[],
        use_blog=False,
    )

    state: AgentState = {
        "query": query,
        "request_id": "blog-eval",
        "tasks": [task],
        "current_task": task.id,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }

    return state





@observe(
    metrics=[
         blog_content_metric,
    ]
)
async def evaluate_blog(
    blog_node: BlogNode,
    golden,
) -> Blog:
    """
    Execute and evaluate BlogNode independently.

    Flow:

        Golden input
             ↓
        AgentState
             ↓
        BlogNode.generate_blog()
             ↓
        Blog artifact
             ↓
        DeepEval metrics
    """

    state = build_blog_state(
        golden
    )

    result = await blog_node.generate_blog(
        state
    )

    

    blog_data = result.get(
        "blog"
    )

    if not blog_data:
        raise AssertionError(
            "BlogNode.generate_blog() did not "
            "produce a blog."
        )

  

    try:
        blog = Blog.model_validate(
            blog_data
        )

    except Exception as exc:
        raise AssertionError(
            "BlogNode.generate_blog() returned "
            "an invalid Blog artifact."
        ) from exc

   

    title = blog.title.strip()

    if not title:
        raise AssertionError(
            "BlogNode.generate_blog() did not "
            "produce a title."
        )

    

    content = blog.content.strip()

    if not content:
        raise AssertionError(
            "BlogNode.generate_blog() did not "
            "produce blog content."
        )

    
    update_current_span(
        test_case=LLMTestCase(
            input=golden.input,
            actual_output=(
                f"TITLE:\n{title}\n\n"
                f"CONTENT:\n{content}"
            ),
        )
    )

    return blog





@pytest.mark.asyncio
@pytest.mark.parametrize(
    "golden",
    dataset.goldens,
)
async def test_blog_component(
    golden,
) -> None:

    blog_node = create_blog_node()

    await evaluate_blog(
        blog_node=blog_node,
        golden=golden,
    )

    assert_test(
        golden=golden,
    )