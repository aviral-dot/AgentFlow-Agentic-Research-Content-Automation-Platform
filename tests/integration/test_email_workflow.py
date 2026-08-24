import pytest


def test_approved_email_routes_to_send(graph_builder):
    """
    Approval must route the workflow to the email sending step.
    """

    state = {
        "approval": "approve"
    }

    result = graph_builder.route_after_approval(state)

    assert result == "send"


def test_rejected_email_routes_to_end(graph_builder):
    """
    Rejection must terminate the email workflow.
    """

    state = {
        "approval": "reject"
    }

    result = graph_builder.route_after_approval(state)

    assert result == "end"


def test_invalid_approval_does_not_send(graph_builder):
    """
    Invalid approval decisions must never route to the
    external email side effect.
    """

    state = {
        "approval": "invalid"
    }

    result = graph_builder.route_after_approval(state)

    assert result != "send"