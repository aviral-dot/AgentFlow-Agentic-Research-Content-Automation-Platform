from uuid import UUID, uuid4

from src.auth.password import hash_password, verify_password
from src.auth.security import create_access_token
from src.auth.user_repository import create_user, get_user_by_email


async def register_user(
    email: str,
    password: str,
) -> dict:
    email = email.strip().lower()

    existing_user = await get_user_by_email(email)

    if existing_user is not None:
        raise ValueError("A user with this email already exists.")

    user_id = uuid4()
    password_hash = hash_password(password)

    user = await create_user(
        user_id=user_id,
        email=email,
        password_hash=password_hash,
    )

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "is_active": user["is_active"],
    }


async def authenticate_user(
    email: str,
    password: str,
) -> dict | None:
    email = email.strip().lower()

    user = await get_user_by_email(email)

    if user is None:
        return None

    if not user["is_active"]:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    user_id = UUID(str(user["id"]))

    access_token = create_access_token(user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "is_active": user["is_active"],
        },
    }