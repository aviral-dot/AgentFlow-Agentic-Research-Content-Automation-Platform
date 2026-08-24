import pytest

from langgraph.checkpoint.memory import MemorySaver


@pytest.mark.asyncio
async def test_graph_uses_checkpointer(
    fake_llm,
):
    """
    Verify that the graph can be compiled with a checkpointer.

    This is important because the application relies on
    state persistence for HITL workflows.
    """

    from src.graphs.graph_builder import GraphBuilder

    checkpointer = MemorySaver()

    builder = GraphBuilder(
        fake_llm,
        checkpointer,
    )

    graph = builder.setup_graph()

    assert graph is not None