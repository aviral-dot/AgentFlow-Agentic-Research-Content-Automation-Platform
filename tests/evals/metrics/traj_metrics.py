import os

from deepeval.metrics import (
    PlanAdherenceMetric,
    PlanQualityMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
)
from deepeval.models import DeepEvalBaseLLM
from langchain_openai import ChatOpenAI

from tests.evals.helpers.eval_model import create_eval_model



eval_model = create_eval_model()


task_completion_metric = TaskCompletionMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)

step_efficiency_metric = StepEfficiencyMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)

plan_quality_metric = PlanQualityMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)

plan_adherence_metric = PlanAdherenceMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)


trajectory_metrics = [
    task_completion_metric,
    step_efficiency_metric,
    plan_quality_metric,
    plan_adherence_metric,
]