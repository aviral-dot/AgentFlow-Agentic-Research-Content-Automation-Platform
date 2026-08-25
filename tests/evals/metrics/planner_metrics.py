from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from tests.evals.metrics.agent_metrics import eval_model


plan_quality = GEval(
    name="Plan Quality",
    criteria=(
        "Evaluate whether the generated execution plan:\n"
        "1. Directly addresses the user's request.\n"
        "2. Contains appropriate tasks for the request.\n"
        "3. Orders tasks logically.\n"
        "4. Uses dependencies correctly.\n"
        "5. Does not contain unnecessary tasks.\n"
        "6. Does not omit required tasks."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    model=eval_model,
)