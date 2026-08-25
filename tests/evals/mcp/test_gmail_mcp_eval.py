from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from tests.evals.helpers.mcp_capture import (
    build_gmail_mcp_server,
    build_send_email_tool_call,
)
from evals.metrics.mcp_metrics import mcp_use_metric


def test_gmail_send_email_mcp():

    query = (
        "Send Rahul an email telling him "
        "to attend school early."
    )

    actual_output = (
        "Email draft created for Rahul."
    )

    tool_call = build_send_email_tool_call(
        to="rahul@example.com",
        subject="School Tomorrow",
        body=(
            "Please attend school early tomorrow."
        ),
    )

    test_case = LLMTestCase(
        input=query,
        actual_output=actual_output,
        mcp_servers=[
            build_gmail_mcp_server(),
        ],
        mcp_tools_called=[
            tool_call,
        ],
    )

    assert_test(
        test_case=test_case,
        metrics=[
            mcp_use_metric,
        ],
    )