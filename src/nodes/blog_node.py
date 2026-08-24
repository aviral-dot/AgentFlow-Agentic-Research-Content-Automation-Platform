# mypy: ignore-errors

import logging
from time import perf_counter

from src.states.blogstate import AgentState
from src.utils.loggers import (
    get_logger,
    log_event,
)

logger = get_logger(__name__)


class BlogNode:

    def __init__(
        self,
        llm,
    ):

        self.llm = llm

        log_event(
            logger,
            level=logging.INFO,
            event="blog_node_initialized",
        )

    # ========================================================
    # CURRENT TASK
    # ========================================================

    def _get_blog_description(
        self,
        state: AgentState,
    ) -> str:

        current_task_id = state.get(
            "current_task"
        )

        if current_task_id:

            for task in state.get(
                "tasks",
                [],
            ):

                if task.id == current_task_id:

                    if task.description.strip():
                        return task.description.strip()

        query = state.get("query")

        if query:
            return query.strip()

        return ""

    # ========================================================
    # TITLE
    # ========================================================

    async def title_creation(
        self,
        state: AgentState,
    ):

        request_id = state.get(
            "request_id"
        )

        description = self._get_blog_description(
            state
        )

        if not description:
            raise ValueError(
                "Blog description is missing."
            )

        prompt = f"""
You are a professional blog writer.

Create a concise, professional and SEO-friendly
title for this blog request:

{description}

Return ONLY the title.
"""

        started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_title_generation_started",
        )

        try:

            response = await self.llm.ainvoke(
                prompt
            )

        except Exception:

            logger.exception(
                "Blog title generation failed"
            )

            raise

        latency_ms = round(
            (perf_counter() - started) * 1000,
            2,
        )

        title = response.content.strip()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_title_generation_completed",
            latency_ms=latency_ms,
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # state["blog"] can explicitly be None.
        #
        # state.get("blog", {}) does NOT protect against that.
        #
        # Therefore use:
        #
        # state.get("blog") or {}
        # ----------------------------------------------------

        blog = dict(
            state.get("blog") or {}
        )

        blog["title"] = title

        return {
            "blog": blog,
        }

    # ========================================================
    # CONTENT
    # ========================================================

    async def content_generation(
        self,
        state: AgentState,
    ):

        request_id = state.get(
            "request_id"
        )

        description = self._get_blog_description(
            state
        )

        if not description:
            raise ValueError(
                "Blog description is missing."
            )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # blog may be None.
        # ----------------------------------------------------

        blog = state.get(
            "blog"
        ) or {}

        title = blog.get(
            "title",
            ""
        )

        if not title:
            raise ValueError(
                "Blog title is missing before content generation."
            )

        prompt = f"""
You are a professional blog writer.

Write a BRIEF but useful blog.

Blog request:
{description}

Title:
{title}

Requirements:

- 250-500 words maximum.
- Keep it concise.
- Use Markdown.
- Use a clear introduction.
- Cover the most important points only.
- Avoid unnecessary repetition.
- Use short sections where appropriate.
- Do not mention AI.
- Do not mention agents.
- Do not mention workflow execution.

Return only the blog content.
"""

        started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_content_generation_started",
        )

        try:

            response = await self.llm.ainvoke(
                prompt
            )

        except Exception:

            logger.exception(
                "Blog content generation failed"
            )

            raise

        latency_ms = round(
            (perf_counter() - started) * 1000,
            2,
        )

        content = response.content.strip()

        blog_result = {
            "title": title,
            "content": content,
        }

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_content_generation_completed",
            latency_ms=latency_ms,
        )

        return {
            "blog": blog_result,
            "task_result": blog_result,
        }