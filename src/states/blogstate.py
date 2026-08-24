from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field





class ResearchResult(BaseModel):
    """
    Research artifact produced by ResearchNode.

    Contains the synthesized research together with
    the important points and source URLs returned
    by the research process.
    """

    topic: str = Field(
        ...,
        min_length=1,
        description="The topic that was researched.",
    )

    summary: str = Field(
        ...,
        min_length=1,
        description="Concise summary of the research.",
    )

    key_points: list[str] = Field(
        ...,
        min_length=1,
        description="Important findings from the research.",
    )

    sources: list[str] = Field(
        default_factory=list,
        description="Source URLs used during research.",
    )





class Blog(BaseModel):
    """
    Generated blog artifact.
    """

    title: str = Field(
        ...,
        min_length=1,
        description="The title of the blog post.",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="The main content of the blog post.",
    )





class Email(BaseModel):
    """
    Generated email artifact.
    """

    to: str = Field(
        ...,
        min_length=1,
        description="Recipient email address.",
    )

    subject: str = Field(
        ...,
        min_length=1,
        description="Email subject.",
    )

    body: str = Field(
        ...,
        min_length=1,
        description="Email body.",
    )





class WorkflowTaskResult(BaseModel):
    """
    Frontend-facing representation of one terminal
    workflow task.

    The result can contain a ResearchResult, Blog,
    Email, or another worker result.
    """

    task_id: str = Field(
        ...,
        min_length=1,
    )

    task_type: Literal[
        "research",
        "blog",
        "email",
    ]

    status: Literal[
        "completed",
        "rejected",
        "failed",
    ]

    result: Any | None = None




class Task(BaseModel):
    """
    Runtime representation of one workflow task.

    Supported workers:

        research
        blog
        email

    Task dependencies determine the execution order.

    Example:

        task_1 = research
        task_2 = blog depends_on task_1
        task_3 = email depends_on task_2
    """

   

    id: str = Field(
        ...,
        min_length=1,
        description="Unique task identifier.",
    )

   

    type: Literal[
        "research",
        "blog",
        "email",
    ] = Field(
        ...,
        description="Worker type responsible for this task.",
    )

    

    description: str = Field(
        ...,
        min_length=1,
        description="Specific action that this task must perform.",
    )

    

    depends_on: list[str] = Field(
        default_factory=list,
        description=(
            "Task IDs that must complete before "
            "this task can execute."
        ),
    )

    

    use_blog: bool = Field(
        default=False,
        description=(
            "True when an email task consumes the "
            "output of a previous blog task."
        ),
    )

   

    status: Literal[
        "pending",
        "running",
        "completed",
        "rejected",
        "failed",
    ] = Field(
        default="pending",
        description="Current task lifecycle status.",
    )

    

    result: Any | None = Field(
        default=None,
        description="Final result produced by this task.",
    )





class AgentState(TypedDict, total=False):

  

    query: str

    request_id: str

    

    tasks: list[Task]

    

    current_task: str | None

    completed_tasks: list[str]

    running_tasks: list[str]

    # --------------------------------------------------------
    # RESULT OF EVERY EXECUTED TASK
    #
    # Example:
    #
    # {
    #     "task_1": ResearchResult,
    #     "task_2": Blog,
    #     "task_3": Email
    # }
    # --------------------------------------------------------

    task_results: dict[str, Any]

    # --------------------------------------------------------
    # RESULT OF CURRENTLY EXECUTING TASK
    # --------------------------------------------------------

    task_result: Any | None

    # ========================================================
    # RESEARCH
    # ========================================================

    research: ResearchResult | None

    # ========================================================
    # BLOG
    # ========================================================

    blog: Blog | None

    # ========================================================
    # EMAIL
    # ========================================================

    email: Email | None

    # ========================================================
    # WORKFLOW OUTPUT
    # ========================================================

    workflow_results: list[WorkflowTaskResult]

    response: str

    tool_result: dict | None

    # ========================================================
    # HUMAN APPROVAL
    # ========================================================

    approval: Literal[
        "approve",
        "reject",
    ] | None