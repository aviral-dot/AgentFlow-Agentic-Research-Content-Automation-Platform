# mypy: ignore-errors

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from tests.evals.metrics.traj_metrics import eval_model


planner_quality = GEval(
    name="Workflow Planner Quality",
    criteria="""
Evaluate whether the generated workflow plan correctly
translates the user's request into the smallest valid
executable workflow.

Evaluate all of the following:

1. Task completeness:
   - Every action explicitly requested by the user is represented.
   - No required action is missing.

2. Task correctness:
   - Each task has the appropriate type:
     research, blog, or email.
   - Task descriptions correctly represent the requested action.

3. Dependency correctness:
   - Dependencies correctly represent the required execution order.
   - Blog tasks may depend on research.
   - Blog-dependent email tasks depend on the blog.
   - Independent email tasks remain independent.
   - Email must not directly depend on research.

4. Unnecessary tasks:
   - The planner should not create tasks that were not requested.

5. Independence:
   - Independent actions should remain independent.

6. Overall workflow validity:
   - The generated plan should represent a logical executable
     workflow without incorrect or unnecessary dependencies.

Give a high score when the workflow accurately represents
the user's request with the minimum necessary tasks.
""",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.7,
    model=eval_model,
)




