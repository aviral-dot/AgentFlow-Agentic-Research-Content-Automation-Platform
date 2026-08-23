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

    def __init__(self, llm):

        self.llm = llm
       
        
        self.email_tool = EmailTool()

        self.structured_llm = (
            llm.with_structured_output(
                EmailDraft,
                method="json_mode",
            )
        )

        log_event(
            logger,
            level=logging.INFO,
            
            event="email_node_initialized",
        )


    async def draft_email(
    self,
    state: AgentState,
    ):

                    query = state["query"]
                
                    request_id = state[
                        "request_id"
                    ]
                
                    current_task_index = state.get(
                        "current_task",
                        0,
                    )
                
                    tasks = state.get(
                        "tasks",
                        [],
                    )
                
                    current_task = None
                
                    if current_task_index < len(tasks):
                
                        current_task = tasks[
                            current_task_index
                        ]
                
                    use_blog = False
                
                    if current_task is not None:
                
                        use_blog = current_task.use_blog
                
                    # ========================================================
                    # BLOG → EMAIL
                    # ========================================================
                
                    if use_blog:
                
                        blog = state.get(
                            "blog"
                        )
                
                        if not blog:
                
                            raise ValueError(
                                "Email task requires a generated "
                                "blog, but no blog exists in state."
                            )
                
                        prompt = f"""
                You are an AI Email Assistant.
                
                The user requested:
                
                {query}
                
                A blog has already been generated.
                
                Blog title:
                {blog["title"]}
                
                The email should send this exact
                generated blog.
                
                Your job is ONLY to determine:
                
                1. Recipient email
                2. Email subject
                
                Do NOT rewrite the blog.
                Do NOT summarize the blog.
                Do NOT modify the blog.
                
                Return ONLY valid JSON:
                
                {{
                    "to": "recipient@example.com",
                    "subject": "Email subject",
                    "body": "BLOG_PLACEHOLDER"
                }}
                
                The body will be replaced by the
                application with the exact generated blog.
                """
                
                    # ========================================================
                    # NORMAL EMAIL
                    # ========================================================
                
                    else:
                
                        prompt = f"""
                You are an AI Email Assistant.
                
                The user request is:
                
                {query}
                
                Extract:
                
                1. Recipient Email
                2. Subject
                3. Email Body
                
                Create the email requested by the user.
                
                Return ONLY valid JSON with exactly
                these fields:
                
                {{
                    "to": "recipient@example.com",
                    "subject": "Email subject",
                    "body": "Email body"
                }}
                
                Do not return markdown.
                Do not return explanations.
                Do not return any text outside the JSON.
                """
                
                    generation_started = perf_counter()
                
                    log_event(
                        logger,
                        level=logging.INFO,
                        request_id=request_id,
                        event="email_draft_generation_started",
                        use_blog=use_blog,
                    )
                
                    try:
                
                        draft = await self.structured_llm.ainvoke(
                            prompt
                        )
                
                    except Exception:
                
                        latency_ms = round(
                            (
                                perf_counter()
                                - generation_started
                            )
                            * 1000,
                            2,
                        )
                
                        logger.exception(
                            "Email draft generation failed",
                            extra={
                                "event": (
                                    "email_draft_generation_failed"
                                ),
                                "context": {
                                    "latency_ms": latency_ms,
                                    "use_blog": use_blog,
                                },
                            },
                            request_id=request_id,
                        )
                
                        raise
                
                    latency_ms = round(
                        (
                            perf_counter()
                            - generation_started
                        )
                        * 1000,
                        2,
                    )
                
                    # ========================================================
                    # BUILD FINAL EMAIL
                    # ========================================================
                
                    if use_blog:
                
                        blog = state["blog"]
                
                        email_body = (
                            f"{blog['title']}\n\n"
                            f"{blog['content']}"
                        )
                
                    else:
                
                        email_body = draft.body
                
                    log_event(
                        logger,
                        level=logging.INFO,
                        event="email_draft_generation_completed",
                        latency_ms=latency_ms,
                        request_id=request_id,
                        use_blog=use_blog,
                        status="success",
                    )
                
                    return {
                        "email": {
                            "to": str(draft.to),
                            "subject": draft.subject,
                            "body": email_body,
                        }
                    }

     
    # ========================================================
    # HUMAN APPROVAL
    # ========================================================

    def approve_email(
        self,
        state: AgentState,
    ):

        email = state["email"]
        request_id = state["request_id"]

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="email_approval_requested"
        )

        decision = interrupt(
            {
                "type": "email_approval",
                "message": (
                    "Please approve or reject "
                    "this email before sending."
                ),
                "email": {
                    "to": email["to"],
                    "subject": email["subject"],
                    "body": email["body"],
                },
            }
        )

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="email_approval_decision_received",
            decision=decision,
        )

        return {
            "approval": decision,
        }

    # ========================================================
    # SEND EMAIL
    # ========================================================

    async def send_email(
        self,
        state: AgentState,
    ):

        email = EmailDraft.model_validate(
            state["email"]
        )
        request_id = state["request_id"]

        send_started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="email_send_started",
        )

        try:

            result = await self.email_tool.send(
                to=str(email.to),
                subject=email.subject,
                body=email.body,
            )

        except Exception:

            latency_ms = round(
                (perf_counter() - send_started) * 1000,
                2,
            )

            logger.exception(
                "Email sending failed",
                request_id=request_id,
                extra={
                    "event": "email_send_failed",
                    "context": {
                        "latency_ms": latency_ms,
                    },
                },
            )

            raise

        latency_ms = round(
            (perf_counter() - send_started) * 1000,
            2,
        )

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="email_send_completed",
            latency_ms=latency_ms,
            status="success",
        )

        return {
            "response": "Email Sent Successfully",
            "tool_result": result,
        }

