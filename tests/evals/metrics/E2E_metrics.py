import os

from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
    TaskCompletionMetric,
)
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import SingleTurnParams
from langchain_openai import ChatOpenAI


class OpenRouterEvalModel(DeepEvalBaseLLM):
    """
    LLM used by DeepEval as the evaluation judge.
    """

    def __init__(self) -> None:
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

    def get_model_name(self) -> str:
        return "OpenRouter Evaluation Model"


eval_model = OpenRouterEvalModel()


task_completion_metric = TaskCompletionMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)


answer_relevancy_metric = AnswerRelevancyMetric(
    threshold=0.80,
    model=eval_model,
    include_reason=True,
)


blog_quality_metric = GEval(
    name="Blog Quality",
    criteria=(
        "Evaluate the final response produced by the complete "
        "AgentFlow workflow. Determine whether it fulfills "
        "the user's request. The response should be relevant "
        "to the requested topic, coherent, useful, well-written, "
        "and satisfy explicit requirements in the user's request. "
        "If the request asks for research-based blog content, "
        "the response should appropriately reflect the requested "
        "topic and produce a concise blog."
    ),
    evaluation_params=[
       SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
    ],
    threshold=0.80,
    model=eval_model,
)


agent_e2e_metrics = [
    task_completion_metric,
    answer_relevancy_metric,
    blog_quality_metric,
]