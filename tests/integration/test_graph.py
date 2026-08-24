import pytest


@pytest.mark.asyncio
async def test_blog_workflow(
    graph_builder,
    thread_config,
):
    """
    End-to-end LangGraph execution for the blog workflow.

    Uses the fake LLM and MemorySaver so the test does not
    require Groq or PostgreSQL.
    """

    graph = graph_builder.setup_graph()

    state = {
        "query": "Write a blog about artificial intelligence"
    }

    result = await graph.ainvoke(
        state,
        config=thread_config,
    )

    assert result is not None

    assert result.get("route") == "blog"