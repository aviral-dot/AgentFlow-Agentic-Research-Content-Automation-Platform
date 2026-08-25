import pytest
from pydantic import ValidationError

from src.states.blogstate import (
    Blog,
    Email,
    ResearchResult,
    Task,
    WorkflowTaskResult,
)


def test_task_defaults():
    task = Task(
        id="task_1",
        type="research",
        description="Research AI agents",
    )

    assert task.status == "pending"
    assert task.depends_on == []
    assert task.use_blog is False
    assert task.result is None


def test_task_accepts_valid_types():
    for task_type in [
        "research",
        "blog",
        "email",
    ]:
        task = Task(
            id=f"{task_type}_1",
            type=task_type,
            description="Do task",
        )

        assert task.type == task_type


def test_task_rejects_empty_id():
    with pytest.raises(
        ValidationError
    ):
        Task(
            id="",
            type="research",
            description="Research",
        )


def test_task_rejects_empty_description():
    with pytest.raises(
        ValidationError
    ):
        Task(
            id="task_1",
            type="research",
            description="",
        )


def test_research_result_requires_topic_summary_and_key_points():
    result = ResearchResult(
        topic="AI agents",
        summary="Agents automate workflows.",
        key_points=[
            "Agents can use tools."
        ],
    )

    assert result.topic == "AI agents"
    assert result.sources == []


def test_blog_requires_title_and_content():
    blog = Blog(
        title="AI Agents",
        content="Blog content",
    )

    assert blog.title == "AI Agents"


def test_email_requires_recipient_subject_and_body():
    email = Email(
        to="user@example.com",
        subject="Hello",
        body="Body",
    )

    assert email.to == "user@example.com"


def test_workflow_task_result_accepts_terminal_status():
    result = WorkflowTaskResult(
        task_id="task_1",
        task_type="email",
        status="rejected",
        result={
            "message": "Rejected"
        },
    )

    assert result.status == "rejected"