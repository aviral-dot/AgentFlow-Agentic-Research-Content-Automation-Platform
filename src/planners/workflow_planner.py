from typing import Literal

from pydantic import BaseModel, Field

from src.states.blogstate import AgentState, Task


# ============================================================
# PLANNED TASK
# ============================================================


class PlannedTask(BaseModel):
    """
    Structured task produced by the workflow planner.

    Supported task types:

        blog
        email

    use_blog=True is allowed only for an email task that
    consumes the output of a previous blog task.
    """

    # --------------------------------------------------------
    # TASK ID
    # --------------------------------------------------------

    id: str = Field(
        ...,
        min_length=1,
        description=(
            "Unique task identifier such as task_1, task_2."
        ),
    )

    # --------------------------------------------------------
    # TASK TYPE
    # --------------------------------------------------------

    type: Literal[
        "blog",
        "email",
    ] = Field(
        ...,
        description=(
            "Task type. Must be exactly 'blog' or 'email'."
        ),
    )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description: str = Field(
        ...,
        min_length=1,
        description=(
            "Specific action that this task must perform."
        ),
    )

    # --------------------------------------------------------
    # DEPENDENCIES
    # --------------------------------------------------------

    depends_on: list[str] = Field(
        ...,
        description=(
            "IDs of tasks that must complete before this "
            "task can execute. Use [] when there is no "
            "dependency."
        ),
    )

    # --------------------------------------------------------
    # BLOG → EMAIL
    # --------------------------------------------------------

    use_blog: bool = Field(
        ...,
        description=(
            "True only when an email task must consume "
            "the generated output of a previous blog task. "
            "False for independent emails and all blog tasks."
        ),
    )


# ============================================================
# WORKFLOW PLAN
# ============================================================


class WorkflowPlan(BaseModel):
    """
    Complete structured workflow returned by the planner.
    """

    tasks: list[PlannedTask] = Field(
        ...,
        description=(
            "Smallest executable set of workflow tasks."
        ),
    )


# ============================================================
# WORKFLOW PLANNER
# ============================================================


class WorkflowPlanner:

    def __init__(
        self,
        llm,
    ):

        self.llm = llm

        # ----------------------------------------------------
        # STRUCTURED OUTPUT
        # ----------------------------------------------------

        self.structured_llm = (
            llm.with_structured_output(
                WorkflowPlan
            )
        )

    # ========================================================
    # PLAN VALIDATION
    # ========================================================

    def validate_plan(
        self,
        tasks: list[PlannedTask],
    ) -> None:
        """
        Validate the planner output before execution.

        Rules:

        1. Workflow cannot be empty.
        2. Task IDs must be unique.
        3. Task IDs cannot be empty.
        4. Task descriptions cannot be empty.
        5. Only blog/email tasks are supported.
        6. Dependencies must reference existing tasks.
        7. Self-dependencies are forbidden.
        8. Blog tasks cannot depend on another task.
        9. Blog tasks cannot use_blog.
        10. Email use_blog=True requires a blog dependency.
        11. Email use_blog=False cannot depend on a blog.
        """

        # ====================================================
        # EMPTY PLAN
        # ====================================================

        if not tasks:

            raise ValueError(
                "Planner returned an empty workflow."
            )

        # ====================================================
        # NORMALIZE TASK IDS
        # ====================================================

        task_ids = [
            task.id.strip()
            for task in tasks
        ]

        # ====================================================
        # UNIQUE TASK IDS
        # ====================================================

        if len(set(task_ids)) != len(task_ids):

            raise ValueError(
                "Planner produced duplicate task IDs."
            )

        # ====================================================
        # TASK MAP
        # ====================================================

        task_map = {
            task.id.strip(): task
            for task in tasks
        }

        # ====================================================
        # VALIDATE EACH TASK
        # ====================================================

        for task in tasks:

            task_id = task.id.strip()

            # ------------------------------------------------
            # ID
            # ------------------------------------------------

            if not task_id:

                raise ValueError(
                    "Planner produced an empty task ID."
                )

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            if not task.description.strip():

                raise ValueError(
                    f"Task '{task_id}' has an empty "
                    "description."
                )

            # ------------------------------------------------
            # NORMALIZE DEPENDENCIES
            # ------------------------------------------------

            dependency_ids = [
                dependency_id.strip()
                for dependency_id in task.depends_on
            ]

            # ------------------------------------------------
            # SELF DEPENDENCY
            # ------------------------------------------------

            if task_id in dependency_ids:

                raise ValueError(
                    f"Task '{task_id}' cannot depend "
                    "on itself."
                )

            # ------------------------------------------------
            # DEPENDENCY EXISTENCE
            # ------------------------------------------------

            for dependency_id in dependency_ids:

                if dependency_id not in task_map:

                    raise ValueError(
                        f"Task '{task_id}' depends on "
                        f"unknown task '{dependency_id}'."
                    )

            # =================================================
            # BLOG TASK
            # =================================================

            if task.type == "blog":

                # --------------------------------------------
                # BLOG CANNOT CONSUME BLOG
                # --------------------------------------------

                if task.use_blog:

                    raise ValueError(
                        f"Blog task '{task_id}' cannot "
                        "have use_blog=True."
                    )

                # --------------------------------------------
                # BLOG SHOULD BE ROOT TASK
                # --------------------------------------------

                if dependency_ids:

                    raise ValueError(
                        f"Blog task '{task_id}' should not "
                        "depend on another task."
                    )

            # =================================================
            # EMAIL TASK
            # =================================================

            elif task.type == "email":

                # --------------------------------------------
                # FIND BLOG DEPENDENCIES
                # --------------------------------------------

                blog_dependencies = [
                    dependency_id
                    for dependency_id in dependency_ids
                    if task_map[
                        dependency_id
                    ].type == "blog"
                ]

                # --------------------------------------------
                # BLOG-DEPENDENT EMAIL
                # --------------------------------------------

                if task.use_blog:

                    if not blog_dependencies:

                        raise ValueError(
                            f"Email task '{task_id}' has "
                            "use_blog=True but does not "
                            "depend on a blog task."
                        )

                # --------------------------------------------
                # INDEPENDENT EMAIL
                # --------------------------------------------

                else:

                    if blog_dependencies:

                        raise ValueError(
                            f"Email task '{task_id}' has "
                            "use_blog=False but depends "
                            "on blog task(s): "
                            f"{blog_dependencies}."
                        )

            # =================================================
            # UNSUPPORTED TASK
            # =================================================

            else:

                raise ValueError(
                    f"Unsupported task type "
                    f"'{task.type}' for task "
                    f"'{task_id}'."
                )

    # ========================================================
    # CYCLE DETECTION
    # ========================================================

    def validate_no_cycles(
        self,
        tasks: list[PlannedTask],
    ) -> None:
        """
        Detect circular dependencies using DFS.
        """

        dependency_graph = {
            task.id.strip(): [
                dependency_id.strip()
                for dependency_id in task.depends_on
            ]
            for task in tasks
        }

        visiting: set[str] = set()

        visited: set[str] = set()

        def visit(
            task_id: str,
        ) -> None:

            # ------------------------------------------------
            # CYCLE
            # ------------------------------------------------

            if task_id in visiting:

                raise ValueError(
                    "Circular dependency detected "
                    f"around task '{task_id}'."
                )

            # ------------------------------------------------
            # ALREADY VALIDATED
            # ------------------------------------------------

            if task_id in visited:

                return

            # ------------------------------------------------
            # DFS ENTER
            # ------------------------------------------------

            visiting.add(
                task_id
            )

            # ------------------------------------------------
            # VISIT DEPENDENCIES
            # ------------------------------------------------

            for dependency_id in dependency_graph.get(
                task_id,
                [],
            ):

                visit(
                    dependency_id
                )

            # ------------------------------------------------
            # DFS EXIT
            # ------------------------------------------------

            visiting.remove(
                task_id
            )

            visited.add(
                task_id
            )

        # ----------------------------------------------------
        # CHECK EVERY TASK
        # ----------------------------------------------------

        for task_id in dependency_graph:

            visit(
                task_id
            )

    # ========================================================
    # PLAN
    # ========================================================

    async def plan(
        self,
        state: AgentState,
    ):
        """
        Convert the user's natural-language request into
        an executable dependency graph.

        Supported workflows:

            1. Blog only
            2. Email only
            3. Blog + independent email
            4. Blog → email
        """

        # ====================================================
        # USER QUERY
        # ====================================================

        query = state.get(
            "query"
        )

        if not query:

            raise ValueError(
                "Cannot create workflow plan because "
                "query is missing."
            )

        # ====================================================
        # PLANNER PROMPT
        # ====================================================

        prompt = f"""
You are a strict workflow planner.

Your job is to convert the user's request into the
SMALLEST executable set of independent tasks.

You MUST NOT execute the tasks.

You ONLY create the workflow plan.

============================================================
SUPPORTED TASK TYPES
============================================================

Only these task types are allowed:

1. blog
2. email

Every task MUST contain:

- id
- type
- description
- depends_on
- use_blog

============================================================
BLOG TASK
============================================================

A blog task generates a BRIEF professional blog.

Default blog length:

250-500 words.

If the user explicitly requests a different length,
follow the user's requested length.

Example:

User:

"Generate a brief blog about NVIDIA."

Plan:

task_1:
    id = "task_1"
    type = "blog"
    description = "Generate a brief blog about NVIDIA"
    depends_on = []
    use_blog = false

A blog task MUST NOT depend on an email task.

A blog task MUST NOT depend on another blog task.

A blog task MUST always have:

depends_on = []

use_blog = false

============================================================
EMAIL TASK
============================================================

An email task sends an email.

There are TWO different email scenarios.

------------------------------------------------------------
SCENARIO A — EMAIL USES GENERATED BLOG
------------------------------------------------------------

If the user wants the generated blog/article/content
itself to be emailed, the email depends on the blog.

Example:

"Generate a brief blog about NVIDIA and email the generated
blog to Rahul."

Plan:

task_1:
    id = "task_1"
    type = "blog"
    description = "Generate a brief blog about NVIDIA"
    depends_on = []
    use_blog = false

task_2:
    id = "task_2"
    type = "email"
    description = "Email the generated blog to Rahul"
    depends_on = ["task_1"]
    use_blog = true

The email MUST wait until task_1 has completed.

------------------------------------------------------------
SCENARIO B — INDEPENDENT EMAIL
------------------------------------------------------------

If the email contains its own unrelated instruction,
the email is completely independent.

Example:

"Generate a brief blog about NVIDIA and email Rahul
telling him to attend school early."

Plan:

task_1:
    id = "task_1"
    type = "blog"
    description = "Generate a brief blog about NVIDIA"
    depends_on = []
    use_blog = false

task_2:
    id = "task_2"
    type = "email"
    description = "Email Rahul telling him to attend school early"
    depends_on = []
    use_blog = false

IMPORTANT:

Do NOT make task_2 depend on task_1.

The fact that both tasks occur in the same user request
does NOT create a dependency.

============================================================
BLOG REFERENCE PHRASES
============================================================

Treat an email as blog-dependent when the user explicitly
asks to send the generated blog, article, or content.

Examples:

- "send the generated blog to Rahul"
- "email the blog to Rahul"
- "send Rahul the blog"
- "email the generated article to Rahul"
- "send the article to Rahul"
- "email this blog to Rahul"
- "send the generated content to Rahul"
- "mail the above blog to Rahul"

In these cases:

use_blog = true

and:

depends_on = ["<blog_task_id>"]

============================================================
INDEPENDENT EMAIL PHRASES
============================================================

Treat an email as independent when it has its own
unrelated instruction.

Examples:

- "email Rahul telling him to go to school early"
- "send Rahul a reminder about the meeting"
- "email Rahul saying the meeting is tomorrow"
- "send Rahul an email asking him to call me"

These emails do NOT consume blog output.

Therefore:

use_blog = false

depends_on = []

============================================================
DEPENDENCY RULES
============================================================

1. Use [] when a task has no dependency.

2. An email may depend on a blog ONLY when the email
   consumes the generated blog.

3. use_blog=true means the email consumes the output of
   a completed blog task.

4. use_blog=true requires a blog dependency.

5. use_blog=false means the email is independent from
   blog output.

6. use_blog=false emails MUST NOT depend on blog tasks.

7. Never create a dependency merely because blog and
   email appear in the same request.

8. Never make a blog depend on an email.

9. Never create a circular dependency.

10. Every dependency must reference an existing task.

11. Independent tasks MUST remain independent.

12. Do not create unnecessary tasks.

13. Do not combine multiple independent actions into
    one task.

============================================================
TASK DESCRIPTION RULES
============================================================

Each task description must describe ONLY the action
belonging to that task.

GOOD:

"Generate a brief blog about NVIDIA"

"Email the generated blog to Rahul"

"Email Rahul telling him to attend school early"

BAD:

"Generate a blog about NVIDIA and email Rahul"

Do not combine blog and email actions into one task.

============================================================
TASK ORDER
============================================================

Prefer deterministic task IDs:

task_1
task_2
task_3

When an email consumes a blog:

blog task first

then dependent email task.

Example:

task_1 → task_2

============================================================
IMPORTANT OUTPUT RULE
============================================================

Return ONLY the structured WorkflowPlan.

Do not return explanations.

Do not return markdown.

Do not return natural-language commentary.

============================================================
USER REQUEST
============================================================

{query}
"""

        # ====================================================
        # GENERATE STRUCTURED PLAN
        # ====================================================

        result = await self.structured_llm.ainvoke(
            prompt
        )

        # ====================================================
        # VALIDATE PLAN
        # ====================================================

        self.validate_plan(
            result.tasks
        )

        self.validate_no_cycles(
            result.tasks
        )

        # ====================================================
        # CONVERT PLANNER TASKS → RUNTIME TASKS
        # ====================================================

        runtime_tasks: list[Task] = []

        for planned_task in result.tasks:

            runtime_tasks.append(
                Task(
                    id=planned_task.id.strip(),
                    type=planned_task.type,
                    description=(
                        planned_task.description.strip()
                    ),
                    depends_on=[
                        dependency_id.strip()
                        for dependency_id
                        in planned_task.depends_on
                    ],
                    use_blog=planned_task.use_blog,
                    status="pending",
                )
            )

        # ====================================================
        # INITIAL WORKFLOW STATE
        # ====================================================

        return {
            "tasks": runtime_tasks,

            "current_task": None,

            "completed_tasks": [],

            "running_tasks": [],

            "task_results": {},

            "task_result": None,

            "approval": None,

            "blog": None,

            "email": None,

            "workflow_results": [],

            "response": "",

            "tool_result": None,
        }