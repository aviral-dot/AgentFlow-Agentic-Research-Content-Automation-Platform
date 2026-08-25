from src.nodes.mail_node import EmailNode


def test_email_approval_interrupt_contract():

    node = object.__new__(EmailNode)

    assert hasattr(
        node,
        "approve_email",
    )

    assert callable(
        node.approve_email,
    )


def test_email_node_contains_send_operation():

    node = object.__new__(EmailNode)

    assert hasattr(
        node,
        "send_email",
    )

    assert callable(
        node.send_email,
    )