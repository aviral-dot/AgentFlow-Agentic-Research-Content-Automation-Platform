from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    ToolCorrectnessMetric,
)


tool_correctness = ToolCorrectnessMetric(
    threshold=0.80,
)


argument_correctness = ArgumentCorrectnessMetric(
    threshold=0.80,
)