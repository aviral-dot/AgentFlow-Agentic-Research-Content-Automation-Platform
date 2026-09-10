# mypy: ignore-errors

import logging
from time import perf_counter

from src.states.blogstate import AgentState, Blog
from src.errors.exceptions import (
    AgentFlowError,
    LLMFailure,
)
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

        # One structured LLM call will now generate
        # both the blog title and the blog content.
        self.structured_llm = (
            llm.with_structured_output(
                Blog,
                method="json_mode",
            )
        )

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

   

    async def generate_blog(
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

Create a complete, concise, useful, professional,
and SEO-friendly blog post for the user's request.

Blog request:
{description}

Use the following research as the primary factual
context for the blog:

{research_context}

Return BOTH:
1. A concise and compelling blog title.
2. The complete blog content.

Requirements for the title:

- Make it relevant to the user's request.
- Make it professional and SEO-friendly.
- Keep it concise.
- Do not mention research.
- Do not mention AI.
- Do not mention agents.
- Do not invent facts.

Requirements for the blog content:

- 250-500 words maximum.
- Keep it concise and useful.
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

Generate the title and content together as one
complete blog artifact.

Return the result as JSON with exactly these fields:
- "title"
- "content"
"""

      

        else:

            prompt = f"""
You are a professional blog writer.

Create a complete, concise, useful, professional,
and SEO-friendly blog post for this request:

{description}

Return BOTH:
1. A concise and compelling blog title.
2. The complete blog content.

Requirements for the title:

- Keep the title concise.
- Make it relevant to the user's request.
- Make it professional and SEO-friendly.
- Do not mention AI.
- Do not mention agents.

Requirements for the blog content:

- 250-500 words maximum.
- Keep it concise and useful.
- Use Markdown.
- Use a clear introduction.
- Cover the most important points only.
- Avoid unnecessary repetition.
- Use short sections where appropriate.
- Do not mention AI.
- Do not mention agents.
- Do not mention workflow execution.

Generate the title and content together as one
complete blog artifact.

Return the result as JSON with exactly these fields:
- "title"
- "content"
"""

      

        started = perf_counter()

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_generation_started",
            research_used=bool(
                research_context
            ),
        )

        try:

            blog = await self.structured_llm.ainvoke(
                prompt
            )

        except AgentFlowError:
           raise

        except Exception as exc:

            logger.exception(
                "Blog generation failed"
            )

            raise LLMFailure(
        context={
            "component": "blog_node",
            "operation": "generation",
        },
    ) from exc

        latency_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

       

        if not isinstance(
            blog,
            Blog,
        ):

            try:

                blog = Blog.model_validate(
                    blog
                )

            except AgentFlowError:
               raise

            except Exception as exc:
                logger.exception(
                   "Invalid structured blog result",
                extra={
                 "request_id": request_id,
                },
            )

            raise LLMFailure(
                context={
                 "component": "blog_node",
                "operation": "result_validation",
                 },
            ) from exc

        # Convert to dictionary so the existing
        # executor/state/email dependency logic
        # remains compatible.
        blog_result = blog.model_dump()

       

        log_event(
            logger,
            level=logging.INFO,
            request_id=request_id,
            event="blog_generation_completed",
            latency_ms=latency_ms,
            research_used=bool(
                research_context
            ),
        )


        return {
            "blog": blog_result,
            "task_result": blog_result,
        }