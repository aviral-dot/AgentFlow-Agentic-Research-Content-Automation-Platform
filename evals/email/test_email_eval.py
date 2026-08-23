import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from evals.email.dataset import dataset
from evals.email.metrics import email_quality_metric


@pytest.mark.asyncio
@pytest.mark.parametrize("golden", dataset.goldens)
async def test_email_quality(golden, email_node):

    result = await email_node.ainvoke(
        {
            "query": golden.input,
        }
    )

    output = result["<YOUR_ACTUAL_EMAIL_DRAFT_KEY>"]

    assert output

    test_case = LLMTestCase(
        input=golden.input,
        actual_output=output,
    )

    assert_test(
        test_case=test_case,
        metrics=[
            email_quality_metric,
        ],
    )