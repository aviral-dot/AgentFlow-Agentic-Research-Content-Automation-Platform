import os

import pytest
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase

from tests.evals.datasets.research_goldens import (
    RESEARCH_GOLDENS,
)


pytestmark = pytest.mark.evals


def _build_research_metric():
    return GEval(
        name="Research Quality",
        criteria=(
            "Evaluate whether the research output is "
            "concise, factually grounded, relevant to "
            "the requested topic, and contains useful "
            "key findings. Penalize unsupported claims, "
            "irrelevant content, repetition, and fabricated "
            "information."
        ),
        evaluation_params=[
            "input",
            "actual_output",
        ],
        threshold=0.7,
    )


@pytest.mark.parametrize(
    "golden",
    RESEARCH_GOLDENS,
)
def test_research_output_quality(golden):
    """
    DeepEval component evaluation for the research
    worker.

    This test expects a generated research artifact
    to be supplied through the environment so the
    evaluation itself does not make an accidental
    external Tavily request.
    """

    output = os.getenv(
        "DEEPEVAL_RESEARCH_OUTPUT"
    )

    if not output:
        pytest.skip(
            "Set DEEPEVAL_RESEARCH_OUTPUT to run "
            "the research quality evaluation."
        )

    test_case = LLMTestCase(
        input=golden["input"],
        actual_output=output,
    )

    metric = _build_research_metric()

    evaluate(
        test_cases=[test_case],
        metrics=[metric],
    )