import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    return database_url


@asynccontextmanager
async def get_connection() -> AsyncIterator[psycopg.AsyncConnection]:
    async with await psycopg.AsyncConnection.connect(
        get_database_url()
    ) as connection:
        yield connection


async def create_users_table() -> None:
    async with get_connection() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(320) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )

        await connection.commit()


async def get_user_by_email(email: str) -> dict | None:
    async with get_connection() as connection:
        async with connection.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    is_active,
                    created_at,
                    updated_at
                FROM users
                WHERE email = %s
                """,
                (email,),
            )

            return await cursor.fetchone()

async def get_user_by_id(user_id) -> dict | None:
    async with get_connection() as connection:
        async with connection.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    is_active,
                    created_at,
                    updated_at
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )

            return await cursor.fetchone()


async def create_user(
    user_id,
    email: str,
    password_hash: str,
) -> dict:
    async with get_connection() as connection:
        async with connection.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                INSERT INTO users (
                    id,
                    email,
                    password_hash
                )
                VALUES (%s, %s, %s)
                RETURNING
                    id,
                    email,
                    password_hash,
                    is_active,
                    created_at,
                    updated_at
                """,
                (user_id, email, password_hash),
            )

            user = await cursor.fetchone()

        await connection.commit()

        if user is None:
            raise RuntimeError("Failed to create user.")

        return user