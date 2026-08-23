from deepeval.metrics import (
    TaskCompletionMetric,
    StepEfficiencyMetric,
)


task_completion_metric = TaskCompletionMetric(
    threshold=0.80,
    include_reason=True,
)


step_efficiency_metric = StepEfficiencyMetric(
    threshold=0.80,
    include_reason=True,
)