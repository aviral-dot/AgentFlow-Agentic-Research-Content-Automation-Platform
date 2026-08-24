# mypy: ignore-errors

import logging
from time import perf_counter

from langgraph.types import interrupt
from pydantic import BaseModel, EmailStr, Field

from src.states.blogstate import AgentState
from src.tools.email_tool import EmailTool
from src.utils.loggers import (
    get_logger,
    log_event,
)

logger = get_logger(__name__)


class EmailDraft(BaseModel):

    model_config = {
        "str_strip_whitespace": True
    }

    to: EmailStr

    subject: str = Field(
        min_length=1,
        max_length=200,
    )

    body: str = Field(
        min_length=1,
        max_length=10000,
    )


class EmailNode:

    def __init__(
        self,
        llm,
    ):

        self.llm = llm

        self.email_tool = EmailTool()

        self.structured_llm = (
            llm.with_structured_output(
                EmailDraft,
                method="json_mode",
            )
        )

    # ========================================================
    # CURRENT TASK
    # ========================================================

    def get_current_task(
        self,
        state: AgentState,
    ):

        task_id = state.get(
            "current_task"
        )

        if not task_id:
            return None

        for task in state.get(
            "tasks",
            [],
        ):

            if task.id == task_id:
                return task

        return None

    # ========================================================
    # BLOG DEPENDENCY
    # ========================================================

    def get_blog_dependency(
        self,
        state: AgentState,
        current_task,
    ):

        if not current_task.use_blog:
            return None

        for dependency_id in current_task.depends_on:

            dependency_task = next(
                (
                    task
                    for task in state.get(
                        "tasks",
                        [],
                    )
                    if task.id == dependency_id
                ),
                None,
            )

            if dependency_task is None:
                continue

            if dependency_task.type != "blog":
                continue

            blog = state.get(
                "task_results",
                {},
            ).get(
                dependency_id
            )

            if not blog:
                raise ValueError(
                    f"Blog dependency '{dependency_id}' "
                    "has no result."
                )

            if not isinstance(
                blog,
                dict,
            ):
                raise ValueError(
                    "Blog dependency result must be a dictionary."
                )

            if not blog.get("title"):
                raise ValueError(
                    "Blog result is missing title."
                )

            if not blog.get("content"):
                raise ValueError(
                    "Blog result is missing content."
                )

            return blog

        raise ValueError(
            f"Email task '{current_task.id}' requires "
            "a blog dependency."
        )

    # ========================================================
    # DRAFT
    # ========================================================

    async def draft_email(
        self,
        state: AgentState,
    ):

        request_id = state.get(
            "request_id"
        )

        current_task = self.get_current_task(
            state
        )

        if current_task is None:
            raise ValueError(
                "No current email task exists."
            )

        if current_task.type != "email":
            raise ValueError(
                "Current task is not an email task."
            )

        blog = self.get_blog_dependency(
            state,
            current_task,
        )

        # ----------------------------------------------------
        # BLOG → EMAIL
        # ----------------------------------------------------

        if blog is not None:

            prompt = f"""
You are an email assistant.

Create an email for this task:

{current_task.description}

The email must contain the following generated blog
EXACTLY as provided.

BLOG TITLE:
{blog["title"]}

BLOG CONTENT:
{blog["content"]}

Determine only:

1. recipient
2. subject

The application will construct the final email body.

Return JSON:

{{
    "to": "recipient@example.com",
    "subject": "Email subject",
    "body": "placeholder"
}}
"""

        # ----------------------------------------------------
        # INDEPENDENT EMAIL
        # ----------------------------------------------------

        else:

            prompt = f"""
You are an email assistant.

Execute ONLY this email task:

{current_task.description}

Determine:

1. recipient
2. subject
3. email body

Do not perform any other task.

Return JSON only.
"""

        started = perf_counter()

        try:

            draft = await self.structured_llm.ainvoke(
                prompt
            )

        except Exception:

            logger.exception(
                "Email draft generation failed"
            )

            raise

        # ----------------------------------------------------
        # FINAL BODY
        # ----------------------------------------------------

        if blog is not None:

            body = (
                f"{blog['title']}\n\n"
                f"{blog['content']}"
            )

        else:

            body = draft.body

        email = {
            "to": str(draft.to),
            "subject": draft.subject,
            "body": body,
        }

        latency_ms = round(
            (perf_counter() - started) * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="email_draft_generation_completed",
            task_id=current_task.id,
            latency_ms=latency_ms,
        )

        return {
            "email": email,
        }

    # ========================================================
    # APPROVAL
    # ========================================================

    def approve_email(
        self,
        state: AgentState,
    ):

        email = state.get(
            "email"
        )

        if not email:
            raise ValueError(
                "Email draft is missing."
            )

        current_task = self.get_current_task(
            state
        )

        task_id = (
            current_task.id
            if current_task
            else None
        )

        decision = interrupt(
            {
                "type": "email_approval",
                "task_id": task_id,
                "message": (
                    "Please approve or reject "
                    "this email before sending."
                ),
                "email": email,
            }
        )

        if isinstance(
            decision,
            dict,
        ):

            decision = decision.get(
                "decision",
                decision.get("approval"),
            )

        if decision not in {
            "approve",
            "reject",
        }:

            raise ValueError(
                "Invalid approval decision."
            )

        return {
            "approval": decision,
        }

    # ========================================================
    # SEND
    # ========================================================

    async def send_email(
        self,
        state: AgentState,
    ):

        email_data = state.get(
            "email"
        )

        if not email_data:
            raise ValueError(
                "Email draft is missing."
            )

        email = EmailDraft.model_validate(
            email_data
        )

        result = await self.email_tool.send(
            to=str(email.to),
            subject=email.subject,
            body=email.body,
        )

        email_result = {
            "status": "sent",
            "message": "Email Sent Successfully",
            "to": str(email.to),
            "subject": email.subject,
            "body": email.body,
            "tool_result": result,
        }

        return {
            "email": email_data,
            "response": "Email Sent Successfully",
            "tool_result": result,
            "task_result": email_result,
        }