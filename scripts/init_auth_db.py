import asyncio
import selectors

from src.auth.user_repository import create_users_table


async def main() -> None:
    await create_users_table()
    print("Users table initialized successfully.")


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )