from pydantic import BaseModel, Field

from src.states.blogstate import AgentState, Task


class WorkflowPlan(BaseModel):
    """
    Structured output returned by the planner.
    """

    tasks: list[Task] = Field(
        description=(
            "Ordered list of tasks required "
            "to complete the user request."
        )
    )


class WorkflowPlanner:

    def __init__(self, llm):

        self.llm = llm

        self.structured_llm = (
            llm.with_structured_output(
                WorkflowPlan
            )
        )

    async def plan(
        self,
        state: AgentState,
    ):

        query = state["query"]

        prompt = f"""
You are the workflow planner for AgentFlow.

The application supports exactly two task types:

1. blog
   Generate a blog.

2. email
   Draft and send an email.

Your job is to convert the user's request
into the MINIMUM ordered list of tasks.

IMPORTANT RULES:

1. Only create a blog task if the user asks
   to create, write, generate, or produce a blog.

2. Only create an email task if the user asks
   to send, draft, compose, or write an email.

3. A normal email request must NOT create
   a blog task.

4. If the user asks to generate a blog and
   send that generated blog by email:

   - create blog first
   - create email second
   - set use_blog=true on the email task

5. If the user asks to generate a blog and
   send a separate email about the blog,
   set use_blog=false.

6. Keep tasks in execution order.

7. Never create unnecessary tasks.

Examples:

User:
"Generate a blog about AI"

Tasks:
[
  {{
    "id": "task_1",
    "type": "blog",
    "use_blog": false,
    "status": "pending"
  }}
]

User:
"Send an email to xyz@gmail.com saying
I am going to school"

Tasks:
[
  {{
    "id": "task_1",
    "type": "email",
    "use_blog": false,
    "status": "pending"
  }}
]

User:
"Generate a blog about AI and send it
to xyz@gmail.com"

Tasks:
[
  {{
    "id": "task_1",
    "type": "blog",
    "use_blog": false,
    "status": "pending"
  }},
  {{
    "id": "task_2",
    "type": "email",
    "use_blog": true,
    "status": "pending"
  }}
]

User:
"Generate a blog about AI and email John
that the blog is ready"

Tasks:
[
  {{
    "id": "task_1",
    "type": "blog",
    "use_blog": false,
    "status": "pending"
  }},
  {{
    "id": "task_2",
    "type": "email",
    "use_blog": false,
    "status": "pending"
  }}
]

User request:
{query}
"""

        result = await self.structured_llm.ainvoke(
            prompt
        )

        return {
            "tasks": result.tasks,
            "current_task": 0,
            "completed_tasks": [],
        }