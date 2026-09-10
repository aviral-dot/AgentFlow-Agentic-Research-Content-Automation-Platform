import asyncio
import getpass
import selectors

from src.auth.service import register_user


async def main() -> None:
    print("=== AgentFlow AI - Create Login User ===")

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("❌ Passwords do not match.")
        return  

    try:
        user = await register_user(
            email=email,
            password=password,
        )

        print("\n✅ User created successfully.")
        print(f"Email: {user['email']}")
        print(f"User ID: {user['id']}")

    except ValueError as exc:
        print(f"\n❌ {exc}")


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )

