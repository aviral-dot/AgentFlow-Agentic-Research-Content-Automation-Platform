import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from tests.evals.datasets.blog_goldens import BLOG_TOPICS
from evals.metrics.blog_metrics import (
    blog_quality,
    title_relevancy,
)

from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder


@pytest.fixture(scope="module")
def blog_graph():

    gateway = LLMGateway()

    builder = GraphBuilder(
        llm=gateway.get_llm(),
        checkpointer=None,
    )

    return builder.setup_graph()

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    BLOG_TOPICS,
)
async def test_blog_component(
    blog_graph,
    query,
):

    result = await blog_graph.ainvoke(
        {
            "query": query,
        }
    )

    blog = result.get("blog")

    assert blog is not None

    title = blog["title"]
    content = blog["content"]

    assert title.strip()
    assert content.strip()

    title_case = LLMTestCase(
        input=query,
        actual_output=title,
    )

    assert_test(
        test_case=title_case,
        metrics=[
            title_relevancy,
        ],
    )

    content_case = LLMTestCase(
        input=query,
        actual_output=content,
    )

    assert_test(
        test_case=content_case,
        metrics=[
            blog_quality,
        ],
    )