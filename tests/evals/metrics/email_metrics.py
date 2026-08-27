from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from tests.evals.metrics.traj_metrics import eval_model

email_quality = GEval(
    name="Email Quality",
    criteria=(
        "Evaluate whether the generated email appropriately "
        "fulfills the user's requested email task. The email "
        "should be professional, relevant, clear, concise, "
        "and appropriate for the requested purpose."
    ),
    evaluation_steps=[
        (
            "Verify that the email fulfills the user's "
            "requested purpose."
        ),
        (
            "Assess whether the email is relevant to "
            "the user's request."
        ),
        (
            "Assess whether the email has a professional "
            "and appropriate tone."
        ),
        (
            "Assess whether the subject is clear and "
            "relevant to the email."
        ),
        (
            "Assess whether the body is clear, concise, "
            "and well written."
        ),
        (
            "Assess whether the generated recipient address "
            "is a valid and appropriate email address."
        ),
    ],
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.7,
    model = eval_model
)




