from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


# ============================================================
# BLOG
# ============================================================


class Blog(BaseModel):
    """
    Generated blog artifact.
    """

    title: str = Field(
        min_length=1,
        description="The title of the blog post.",
    )

    content: str = Field(
        min_length=1,
        description="The main content of the blog post.",
    )


# ============================================================
# EMAIL
# ============================================================


class Email(BaseModel):
    """
    Generated email artifact.
    """

    to: str = Field(
        min_length=1,
        description="Recipient email address.",
    )

    subject: str = Field(
        min_length=1,
        description="Email subject.",
    )

    body: str = Field(
        min_length=1,
        description="Email body.",
    )


# ============================================================
# WORKFLOW TASK RESULT
# ============================================================


class WorkflowTaskResult(BaseModel):
    """
    Frontend-facing representation of one terminal
    workflow task.
    """

    task_id: str = Field(
        min_length=1,
    )

    task_type: Literal[
        "blog",
        "email",
    ]

    status: Literal[
        "completed",
        "rejected",
        "failed",
    ]

    result: Any | None = None


# ============================================================
# TASK
# ============================================================


class Task(BaseModel):
    """
    Runtime representation of one workflow task.

    Lifecycle:

        pending
            ↓
        running
            ↓
        completed

    or:

        running → rejected

    or:

        running → failed
    """

    id: str = Field(
        min_length=1,
    )

    type: Literal[
        "blog",
        "email",
    ]

    description: str = Field(
        min_length=1,
    )

    depends_on: list[str] = Field(
        default_factory=list,
    )

    use_blog: bool = False

    status: Literal[
        "pending",
        "running",
        "completed",
        "rejected",
        "failed",
    ] = "pending"

    # IMPORTANT:
    # Keep the final result on the task itself.
    result: Any | None = None


# ============================================================
# AGENT STATE
# ============================================================


class AgentState(TypedDict, total=False):

    # --------------------------------------------------------
    # USER REQUEST
    # --------------------------------------------------------

    query: str

    request_id: str

    # --------------------------------------------------------
    # PLANNER
    # --------------------------------------------------------

    tasks: list[Task]

    # --------------------------------------------------------
    # EXECUTOR
    # --------------------------------------------------------

    current_task: str | None

    completed_tasks: list[str]

    running_tasks: list[str]

    task_results: dict[str, Any]

    # Result produced by the currently executing worker.
    task_result: Any | None

    # --------------------------------------------------------
    # BLOG
    # --------------------------------------------------------

    blog: Blog | None

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    email: Email | None

    # --------------------------------------------------------
    # WORKFLOW OUTPUT
    # --------------------------------------------------------

    workflow_results: list[WorkflowTaskResult]

    response: str

    tool_result: dict | None

    # --------------------------------------------------------
    # HUMAN APPROVAL
    # --------------------------------------------------------

    approval: Literal[
        "approve",
        "reject",
    ] | None