from deepeval.metrics import MCPUseMetric

from tests.evals.metrics.agent_metrics import eval_model


mcp_use_metric = MCPUseMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)