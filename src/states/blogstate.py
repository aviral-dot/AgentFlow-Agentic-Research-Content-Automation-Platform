# from typing import TypedDict

# from pydantic import BaseModel, Field


# class Blog(BaseModel):
#     title:str=Field(description="the title of the blog post")
#     content:str=Field(description="The main content of the blog post")

# class Email(BaseModel):
#     to: str
#     subject: str
#     body: str

# class AgentState(TypedDict):
#     query: str              

#     route: str              

#     blog: Blog

#     email: Email

#     response: str

#     tool_result: dict

#     request_id: str

#     approval: str


from typing import Literal, TypedDict

from pydantic import BaseModel, Field


class Blog(BaseModel):
    title: str = Field(
        description="The title of the blog post"
    )
    content: str = Field(
        description="The main content of the blog post"
    )


class Email(BaseModel):
    to: str
    subject: str
    body: str


class Task(BaseModel):
    """
    A single unit of work in the workflow.
    """

    id: str

    type: Literal[
        "blog",
        "email",
    ]

    use_blog: bool = False

    status: Literal[
        "pending",
        "completed",
    ] = "pending"


class AgentState(TypedDict, total=False):

    # Original user request
    query: str

    # Request correlation
    request_id: str

    # Planner output
    tasks: list[Task]

    # Current task index
    current_task: int

    # Completed task types
    completed_tasks: list[str]

    # Generated artifacts
    blog: Blog
    email: Email

    # Workflow output
    response: str

    # External tool output
    tool_result: dict

    # HITL decision
    approval: str
