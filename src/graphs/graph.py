# import logging

# from src.database.postgres import create_checkpointer
# from src.gateway.llm_gateway import LLMGateway
# from src.graphs.graph_builder import GraphBuilder
# from src.utils.loggers import (
#     get_logger,
#     log_event,
# )


# logger = get_logger(__name__)




# log_event(
#     logger,
#     level=logging.INFO,
#     event="llm_gateway_initialization_started",
# )

# gateway = LLMGateway()

# llm = gateway.get_llm()

# log_event(
#     logger,
#     level=logging.INFO,
#     event="llm_gateway_initialized",
# )



# log_event(
#     logger,
#     level=logging.INFO,
#     event="checkpointer_initialization_started",
# )

# checkpointer = create_checkpointer()

# log_event(
#     logger,
#     level=logging.INFO,
#     event="checkpointer_initialized",
# )




# log_event(
#     logger,
#     level=logging.INFO,
#     event="graph_builder_initialization_started",
# )

# graph_builder = GraphBuilder(
#     llm=llm,
#     checkpointer=checkpointer,
# )

# log_event(
#     logger,
#     level=logging.INFO,
#     event="graph_builder_initialized",
# )




# log_event(
#     logger,
#     level=logging.INFO,
#     event="graph_compilation_started",
# )

# graph = graph_builder.setup_graph()

# log_event(
#     logger,
#     level=logging.INFO,
#     event="graph_compilation_completed",
#     status="success",
# )



# mypy: ignore-errors

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from src.database.postgres import create_checkpointer
from src.gateway.llm_gateway import LLMGateway
from src.graphs.graph_builder import GraphBuilder
from src.utils.loggers import (
    get_logger,
    log_event,
)


logger = get_logger(__name__)


@asynccontextmanager
async def create_graph() -> AsyncIterator:
    """
    Create the AgentFlow graph with an async PostgreSQL checkpointer.

    The checkpointer remains alive for the entire lifetime of the graph.
    """

    # ============================================================
    # LLM GATEWAY
    # ============================================================

    log_event(
        logger,
        level=logging.INFO,
        event="llm_gateway_initialization_started",
    )

    gateway = LLMGateway()

    llm = gateway.get_llm()

    log_event(
        logger,
        level=logging.INFO,
        event="llm_gateway_initialized",
    )

    # ============================================================
    # CHECKPOINTER
    # ============================================================

    log_event(
        logger,
        level=logging.INFO,
        event="checkpointer_initialization_started",
    )

    async with create_checkpointer() as checkpointer:

        log_event(
            logger,
            level=logging.INFO,
            event="checkpointer_initialized",
        )

        # ========================================================
        # GRAPH BUILDER
        # ========================================================

        log_event(
            logger,
            level=logging.INFO,
            event="graph_builder_initialization_started",
        )

        graph_builder = GraphBuilder(
            llm=llm,
            checkpointer=checkpointer,
        )

        log_event(
            logger,
            level=logging.INFO,
            event="graph_builder_initialized",
        )

        # ========================================================
        # GRAPH COMPILATION
        # ========================================================

        log_event(
            logger,
            level=logging.INFO,
            event="graph_compilation_started",
        )

        graph = graph_builder.setup_graph()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_compilation_completed",
            status="success",
        )

        # ========================================================
        # KEEP CHECKPOINTER ALIVE
        # ========================================================

        yield graph

