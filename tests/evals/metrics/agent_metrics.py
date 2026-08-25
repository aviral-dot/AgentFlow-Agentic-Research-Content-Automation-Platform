import os

from deepeval.metrics import (
    PlanAdherenceMetric,
    PlanQualityMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
)
from deepeval.models import DeepEvalBaseLLM
from langchain_openai import ChatOpenAI


class OpenRouterEvalModel(DeepEvalBaseLLM):

    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv(
                "DEEPEVAL_MODEL",
                "openai/gpt-oss-20b",
            ),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            max_tokens=4096,
            temperature=0,
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        response = self.model.invoke(prompt)
        return response.content

    async def a_generate(self, prompt: str) -> str:
        response = await self.model.ainvoke(prompt)
        return response.content

    def get_model_name(self):
        return "OpenRouter Evaluation Model"


eval_model = OpenRouterEvalModel()


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