import pytest

from src.states.blogstate import Task
from src.executors.workflow_executor import WorkflowExecutor


def build_full_workflow_state():
    tasks = [
        Task(
            id="research_1",
            type="research",
            description="Research the requested topic",
            depends_on=[],
            use_blog=False,
            status="pending",
        ),
        Task(
            id="blog_1",
            type="blog",
            description="Generate a blog from the research",
            depends_on=["research_1"],
            use_blog=False,
            status="pending",
        ),
        Task(
            id="email_1",
            type="email",
            description="Email the generated blog",
            depends_on=["blog_1"],
            use_blog=True,
            status="pending",
        ),
    ]

    return {
        "tasks": tasks,
        "current_task": None,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }


def test_full_workflow_dependency_chain():
    """
    Verify that the executor respects the complete
    Research -> Blog -> Email dependency chain.
    """

    state = build_full_workflow_state()
    executor = WorkflowExecutor()

    # ---------------------------------------------------------
    # Research must be the first executable task.
    # ---------------------------------------------------------
    task = executor.get_next_task(state)

    assert task is not None
    assert task.id == "research_1"

    # ---------------------------------------------------------
    # Complete research.
    # ---------------------------------------------------------
    state.update(
        executor.mark_task_running(
            state,
            "research_1",
        )
    )

    research_result = {
        "summary": "Research completed successfully.",
        "key_findings": [
            "Finding one",
            "Finding two",
        ],
    }

    state.update(
        executor.mark_task_completed(
            state,
            "research_1",
            research_result,
        )
    )

    assert "research_1" in state["completed_tasks"]

    # ---------------------------------------------------------
    # Blog should now become executable.
    # ---------------------------------------------------------
    task = executor.get_next_task(state)

    assert task is not None
    assert task.id == "blog_1"

    # ---------------------------------------------------------
    # Complete blog generation.
    # ---------------------------------------------------------
    state.update(
        executor.mark_task_running(
            state,
            "blog_1",
        )
    )

    blog_result = {
        "title": "AI Agents",
        "content": "Generated blog content.",
    }

    state.update(
        executor.mark_task_completed(
            state,
            "blog_1",
            blog_result,
        )
    )

    assert "blog_1" in state["completed_tasks"]

    # ---------------------------------------------------------
    # Email should now become executable.
    # ---------------------------------------------------------
    task = executor.get_next_task(state)

    assert task is not None
    assert task.id == "email_1"


def test_full_workflow_does_not_skip_dependencies():
    """
    Verify that downstream tasks cannot execute before
    their dependencies are completed.
    """

    state = build_full_workflow_state()
    executor = WorkflowExecutor()

    task = executor.get_next_task(state)

    assert task.id == "research_1"

    # Blog must NOT be selected before research completes.
    assert (
        state["tasks"][1].status
        == "pending"
    )

    # Email must NOT be selected before blog completes.
    assert (
        state["tasks"][2].status
        == "pending"
    )


def test_full_workflow_reaches_email_after_blog_completion():
    """
    Verify that the complete dependency chain reaches
    the email task after research and blog completion.
    """

    state = build_full_workflow_state()
    executor = WorkflowExecutor()

    # Complete research.
    state.update(
        executor.mark_task_running(
            state,
            "research_1",
        )
    )

    state.update(
        executor.mark_task_completed(
            state,
            "research_1",
            {
                "summary": "Research result",
            },
        )
    )

    # Complete blog.
    state.update(
        executor.mark_task_running(
            state,
            "blog_1",
        )
    )

    state.update(
        executor.mark_task_completed(
            state,
            "blog_1",
            {
                "title": "AI Agents",
                "content": "Generated content",
            },
        )
    )

    # Email must now be the next task.
    next_task = executor.get_next_task(
        state
    )

    assert next_task is not None
    assert next_task.id == "email_1"


def test_full_workflow_preserves_task_results():
    """
    Verify that results produced by upstream tasks
    remain available for downstream workflow stages.
    """

    state = build_full_workflow_state()
    executor = WorkflowExecutor()

    research_result = {
        "summary": "Research summary",
        "key_findings": [
            "Finding one",
            "Finding two",
        ],
    }

    state.update(
        executor.mark_task_running(
            state,
            "research_1",
        )
    )

    state.update(
        executor.mark_task_completed(
            state,
            "research_1",
            research_result,
        )
    )

    assert (
        state["task_results"]["research_1"]
        == research_result
    )

    blog_result = {
        "title": "AI Agents",
        "content": "Generated blog",
    }

    state.update(
        executor.mark_task_running(
            state,
            "blog_1",
        )
    )

    state.update(
        executor.mark_task_completed(
            state,
            "blog_1",
            blog_result,
        )
    )

    assert (
        state["task_results"]["blog_1"]
        == blog_result
    )


def test_full_workflow_completion():
    """
    Verify that the executor recognizes the workflow
    as complete once all tasks reach terminal states.
    """

    state = build_full_workflow_state()
    executor = WorkflowExecutor()

    for task_id, result in [
        (
            "research_1",
            {
                "summary": "Research",
            },
        ),
        (
            "blog_1",
            {
                "title": "AI Agents",
                "content": "Blog",
            },
        ),
        (
            "email_1",
            {
                "message_id": "test-message",
            },
        ),
    ]:
        state.update(
            executor.mark_task_running(
                state,
                task_id,
            )
        )

        state.update(
            executor.mark_task_completed(
                state,
                task_id,
                result,
            )
        )

    assert executor.is_complete(state)