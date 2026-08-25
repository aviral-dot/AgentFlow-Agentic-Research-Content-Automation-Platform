from tests.unit.helpers.fake_email_tool import (
    FakeEmailTool,
)


async def execute_after_approval(
    *,
    decision: str,
    email_tool: FakeEmailTool,
    to: str,
    subject: str,
    body: str,
):
    """
    Evaluation-only representation of the final
    human approval boundary.

    The actual production graph handles the LangGraph
    interrupt. This test verifies the safety contract
    after the decision is obtained.
    """

    if decision == "reject":

        return {
            "status": "rejected",
            "sent": False,
        }

    if decision != "approve":

        raise ValueError(
            "Invalid approval decision."
        )

    result = await email_tool.send(
        to=to,
        subject=subject,
        body=body,
    )

    return {
        "status": "sent",
        "sent": True,
        "result": result,
    }


async def test_rejected_email_is_never_sent():

    email_tool = FakeEmailTool()

    result = await execute_after_approval(
        decision="reject",
        email_tool=email_tool,
        to="rahul@example.com",
        subject="School",
        body="Please attend school early.",
    )

    assert result["status"] == "rejected"

    assert result["sent"] is False

    assert email_tool.send_count == 0


async def test_approved_email_is_sent():

    email_tool = FakeEmailTool()

    result = await execute_after_approval(
        decision="approve",
        email_tool=email_tool,
        to="rahul@example.com",
        subject="School",
        body="Please attend school early.",
    )

    assert result["status"] == "sent"

    assert result["sent"] is True

    assert email_tool.send_count == 1


async def test_approved_email_contains_correct_data():

    email_tool = FakeEmailTool()

    await execute_after_approval(
        decision="approve",
        email_tool=email_tool,
        to="rahul@example.com",
        subject="School",
        body="Please attend school early.",
    )

    sent_email = email_tool.last_call

    assert sent_email is not None

    assert sent_email["to"] == (
        "rahul@example.com"
    )

    assert sent_email["subject"] == "School"

    assert sent_email["body"] == (
        "Please attend school early."
    )


async def test_invalid_approval_cannot_send():

    email_tool = FakeEmailTool()

    try:

        await execute_after_approval(
            decision="invalid",
            email_tool=email_tool,
            to="rahul@example.com",
            subject="School",
            body="Please attend school early.",
        )

    except ValueError:

        pass

    else:

        raise AssertionError(
            "Invalid approval decision was accepted."
        )

    assert email_tool.send_count == 0