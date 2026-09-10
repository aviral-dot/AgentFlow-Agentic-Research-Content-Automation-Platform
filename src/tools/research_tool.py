import logging
import os
from time import perf_counter
from typing import Any


from tavily import AsyncTavilyClient

from src.errors.exceptions import (
    AgentFlowError,
    ResearchFailure,
)

from src.utils.loggers import (
    get_logger,
    log_event,
)


logger = get_logger(__name__)


class ResearchTool:
    """
    Tavily-powered web research tool.

    Responsibilities:
        - Execute web searches using Tavily.
        - Return normalized research results.
        - Keep external search logic outside ResearchNode.
    """

    def __init__(
        self,
    ):

        api_key = os.getenv(
            "TAVILY_API_KEY"
        )

        if not api_key:

            raise ResearchFailure(
        context={
            "component": "tavily",
            "reason": "api_key_not_configured",
        },
    )

        self.client = AsyncTavilyClient(
            api_key=api_key
        )

  

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """
        Search the web using Tavily.

        Args:
            query:
                Research query.

            max_results:
                Maximum number of search results.

        Returns:
            Normalized research result containing:
                - query
                - answer
                - sources
        """

        query = query.strip()

        if not query:

            raise ValueError(
                "Research query cannot be empty."
            )

        if max_results < 1:

            raise ValueError(
                "max_results must be greater than zero."
            )

        started = perf_counter()

        try:

            response = await self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
            )

        except AgentFlowError:
              raise
        
        except Exception as exc:

            logger.exception(
                "Tavily research failed",
                extra={
                    "event": "tavily_research_failed",
                    "query": query,
                },
            )

            raise ResearchFailure(
                context={
                "component": "tavily",
                 "operation": "search",
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

       



        raw_results = response.get(
            "results",
            [],
        )

        sources = []

        for result in raw_results:

            sources.append(
                {
                    "title": result.get(
                        "title",
                        "",
                    ),
                    "url": result.get(
                        "url",
                        "",
                    ),
                    "content": result.get(
                        "content",
                        "",
                    ),
                    "score": result.get(
                        "score",
                    ),
                }
            )

        research_result = {
            "query": query,
            "answer": response.get(
                "answer",
                "",
            ),
            "sources": sources,
        }

        log_event(
            logger,
            level=logging.INFO,
            event="research_tool_completed",
            query=query,
            source_count=len(sources),
            latency_ms=latency_ms,
            status="success",
        )

        return research_result