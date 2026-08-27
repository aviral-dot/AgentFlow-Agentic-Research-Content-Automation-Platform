from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams
from tests.evals.helpers.eval_model import create_eval_model


eval_model = create_eval_model()


blog_content_metric = GEval(
    name="Blog Content Quality",
    criteria="""
Evaluate the generated blog content.

The content should:

1. Be directly relevant to the user's requested topic.
2. Be useful and informative.
3. Be clear and easy to understand.
4. Have a logical structure.
5. Use concise explanations.
6. Avoid unnecessary repetition.
7. Stay focused on the requested topic.
8. Avoid unsupported factual claims.
9. Follow the requested blog-writing requirements.
10. Avoid mentioning internal workflow execution, agents,
    Tavily, or the research process unless explicitly requested.
""",
    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
    ],
    threshold=0.7,
    model=eval_model,
)