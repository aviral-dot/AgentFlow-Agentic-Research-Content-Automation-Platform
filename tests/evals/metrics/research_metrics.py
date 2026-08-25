from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from tests.evals.metrics.agent_metrics import eval_model

research_quality = GEval(
    name="Research Quality",
    criteria=(
        "Evaluate whether the research output directly addresses "
        "the requested topic, provides useful and sufficiently "
        "informative information, remains focused on the request, "
        "and avoids irrelevant or unsupported claims."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    model=eval_model,
)