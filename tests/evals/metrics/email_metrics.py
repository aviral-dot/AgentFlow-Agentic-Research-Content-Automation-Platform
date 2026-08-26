from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from tests.evals.metrics.traj_metrics import eval_model


email_quality = GEval(
    name="Email Quality",
    criteria=(
        "Evaluate the generated email against the user's request. "
        "The email must fulfill the requested purpose, preserve "
        "important user instructions, use an appropriate professional "
        "tone, be concise and coherent, avoid unsupported or "
        "fabricated details, and contain no unresolved placeholders."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    model=eval_model,
)