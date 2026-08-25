from collections.abc import Iterable


def format_email(email) -> str:

    if email is None:
        return ""

    if hasattr(email, "model_dump"):

        email = email.model_dump()

    if isinstance(email, dict):

        return (
            f"To: {email.get('to', '')}\n"
            f"Subject: {email.get('subject', '')}\n"
            f"Body:\n{email.get('body', '')}"
        )

    return str(email)



def format_plan(tasks: Iterable) -> str:
    lines: list[str] = []

    for task in tasks:
        lines.append(
            (
                f"{task.id}: "
                f"type={task.type}; "
                f"description={task.description}; "
                f"depends_on={task.depends_on}; "
                f"use_blog={task.use_blog}"
            )
        )

    return "\n".join(lines)