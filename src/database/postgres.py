import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.errors.exceptions import (
    AgentFlowError,
    DatabaseFailure,
)

from src.utils.loggers import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def create_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
       raise DatabaseFailure(
        context={
            "operation": "checkpointer_setup",
            "reason": "DATABASE_URL_NOT_CONFIGURED",
        },
    )

    try:    
        async with AsyncPostgresSaver.from_conn_string(
            database_url
        ) as checkpointer:
    
            await checkpointer.setup()
    
            yield checkpointer

    except AgentFlowError:
        raise

    except Exception as exc:
        logger.exception(
            "Database initialization failed",
           extra={
            "event": "database_initialization_failed",
           },
        )

        raise DatabaseFailure(
           context={
            "operation": "checkpointer_setup",
           },
        ) from exc