from src.graphs.graph_builder import GraphBuilder


def test_approved_email_routes_to_send():
    builder = object.__new__(GraphBuilder)

    result = builder.route_after_approval(
        {
            "approval": "approve"
        }
    )

    assert result == "send_email"


def test_rejected_email_routes_to_end():
    builder = object.__new__(GraphBuilder)

    result = builder.route_after_approval(
        {
            "approval": "reject"
        }
    )

    assert result == "end"


def test_invalid_approval_routes_to_end():
    builder = object.__new__(GraphBuilder)

    result = builder.route_after_approval(
        {
            "approval": "invalid"
        }
    )

    assert result == "end"