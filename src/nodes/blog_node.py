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

        query = state.get(
            "query"
        )

        if query:

            return query.strip()

        return ""


    

    def _get_research_context(
        self,
        state: AgentState,
    ) -> str:

        research = state.get(
            "research"
        )

        if not research:

            return ""



       

        if hasattr(
            research,
            "model_dump",
        ):

            research_data = research.model_dump()



       
        elif isinstance(
            research,
            dict,
        ):

            research_data = research

        else:

            return ""

        topic = research_data.get(
            "topic",
            "",
        )

        summary = research_data.get(
            "summary",
            "",
        )

        key_points = research_data.get(
            "key_points",
            [],
        )

        sources = research_data.get(
            "sources",
            [],
        )

        context_parts = []

        if topic:

            context_parts.append(
                f"Research Topic:\n{topic}"
            )

        if summary:

            context_parts.append(
                f"Research Summary:\n{summary}"
            )

        if key_points:

            formatted_points = "\n".join(
                f"- {point}"
                for point in key_points
            )

            context_parts.append(
                "Key Research Points:\n"
                f"{formatted_points}"
            )

        if sources:

            formatted_sources = "\n".join(
                f"- {source}"
                for source in sources
            )

            context_parts.append(
                "Research Sources:\n"
                f"{formatted_sources}"
            )

        return "\n\n".join(
            context_parts
        )

    



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

        research_context = (
            self._get_research_context(
                state
            )
        )


       

        if research_context:

            prompt = f"""
You are a professional blog writer.

Create a concise, professional and SEO-friendly
title for the requested blog.

Blog request:
{description}

Use the following research as factual context:

{research_context}

Requirements:

- Make the title relevant to the user's request.
- Use the research to understand the topic.
- Keep the title concise.
- Do not invent facts.
- Do not mention research.
- Do not mention AI.
- Do not mention agents.
- Return ONLY the title.
"""

        else:

            prompt = f"""
You are a professional blog writer.

Create a concise, professional and SEO-friendly
title for this blog request:

{description}

Requirements:

- Keep the title concise.
- Make it relevant to the user's request.
- Do not mention AI.
- Do not mention agents.
- Return ONLY the title.
"""

        started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_title_generation_started",
            research_used=bool(
                research_context
            ),
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
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        title = response.content.strip()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_title_generation_completed",
            latency_ms=latency_ms,
            research_used=bool(
                research_context
            ),
        )


        

        blog = dict(
            state.get("blog") or {}
        )

        blog["title"] = title

        return {
            "blog": blog,
        }

  



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



        

        blog = state.get(
            "blog"
        ) or {}

        title = blog.get(
            "title",
            "",
        )

        if not title:

            raise ValueError(
                "Blog title is missing before "
                "content generation."
            )


        

        research_context = (
            self._get_research_context(
                state
            )
        )


        

        if research_context:

            prompt = f"""
You are a professional blog writer.

Write a BRIEF, useful and factually grounded blog.

Blog request:
{description}

Title:
{title}

Use the following research as the primary
factual context:

{research_context}

Requirements:

- 250-500 words maximum.
- Keep it concise.
- Use Markdown.
- Use a clear introduction.
- Cover the most important points only.
- Use the research information provided.
- Do not invent unsupported facts.
- Avoid unnecessary repetition.
- Use short sections where appropriate.
- Do not mention the research process.
- Do not mention Tavily.
- Do not mention AI.
- Do not mention agents.
- Do not mention workflow execution.

Return only the blog content.
"""

       

        else:

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
            research_used=bool(
                research_context
            ),
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
            (
                perf_counter()
                - started
            )
            * 1000,
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
            research_used=bool(
                research_context
            ),
        )

        

        return {
            "blog": blog_result,
            "task_result": blog_result,
        }