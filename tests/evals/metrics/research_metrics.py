
from tests.evals.metrics.traj_metrics import eval_model

from deepeval.metrics import (
    AnswerRelevancyMetric,
)


# ============================================================
# RESEARCH RELEVANCY
# ============================================================

research_relevancy = AnswerRelevancyMetric(
    threshold=0.7,
    model=eval_model,
)


