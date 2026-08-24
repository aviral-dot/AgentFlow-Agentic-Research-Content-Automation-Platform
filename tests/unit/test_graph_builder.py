import pytest


def test_graph_can_be_created(graph_builder):
    """
    GraphBuilder should successfully compile the graph
    with the test checkpointer.
    """

    graph = graph_builder.setup_graph()

    assert graph is not None


def test_graph_contains_nodes(graph_builder):
    """
    Verify that the important application nodes are present.

    This catches accidental graph-topology regressions.
    """

    graph = graph_builder.setup_graph()

    nodes = graph.nodes

    assert "supervisor" in nodes
    assert "blog" in nodes
    assert "email" in nodes


def test_route_blog_request(graph_builder):
    """
    A blog request should be routed to the blog workflow.
    """

    state = {
        "query": "Write a blog about artificial intelligence"
    }

    route = graph_builder.route_request(state)

    assert route == "blog"


def test_route_email_request(graph_builder):
    """
    An email request should be routed to the email workflow.
    """

    state = {
        "query": (
            "Send an email to test@example.com "
            "about tomorrow's meeting"
        )
    }

    route = graph_builder.route_request(state)

    assert route == "email"


def test_invalid_route_is_rejected(graph_builder):
    """
    Invalid routing decisions should not silently pass
    through the graph.
    """

    state = {
        "query": "This is an unsupported request"
    }

    with pytest.raises(Exception):
        graph_builder.route_request(state)