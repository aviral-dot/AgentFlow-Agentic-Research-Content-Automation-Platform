from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


email_quality_metric = GEval(
    name="Email Quality",
    criteria=(
        "Evaluate the generated email against the user's request. "
        "The email must fulfill the requested purpose, have an "
        "appropriate professional tone, be concise, be coherent, "
        "avoid unsupported or fabricated details, and contain no "
        "unresolved placeholders."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    include_reason=True,
)