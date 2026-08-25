
# # mypy: ignore-errors

# import os

# from langgraph.checkpoint.postgres import PostgresSaver


# def create_checkpointer() -> PostgresSaver:
#     database_url = os.getenv("DATABASE_URL")

#     if not database_url:
#         raise RuntimeError(
#             "DATABASE_URL environment variable is not configured."
#         )

#     checkpointer = PostgresSaver.from_conn_string(
#         database_url
#     )

#     checkpointer.setup()

#     return checkpointer


# mypy: ignore-errors

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


@asynccontextmanager
async def create_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    async with AsyncPostgresSaver.from_conn_string(
        database_url
    ) as checkpointer:

        await checkpointer.setup()

        yield checkpointer