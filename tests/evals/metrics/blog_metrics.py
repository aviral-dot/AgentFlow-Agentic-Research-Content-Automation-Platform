import os

from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCaseParams
from langchain_groq import ChatGroq
from tests.evals.metrics.traj_metrics import eval_model



title_relevancy = AnswerRelevancyMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)


blog_quality = GEval(
    name="Blog Quality",
    criteria=(
        "Evaluate whether the generated blog:\n"
        "1. Directly addresses the requested topic.\n"
        "2. Is relevant to the topic.\n"
        "3. Is coherent and logically organized.\n"
        "4. Provides useful and sufficiently detailed information.\n"
        "5. Is clear and easy to understand.\n"
        "6. Uses appropriate Markdown formatting.\n"
        "7. Avoids unsupported or fabricated claims."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    model=eval_model,
)