from src.executors.task_scheduler import TaskScheduler
from src.executors.workflow_executor import WorkflowExecutor
from src.states.blogstate import Task


def test_planner_executor_dependency_flow():
    tasks = [
        Task(
            id="task_1",
            type="research",
            description="Research AI agents",
        ),
        Task(
            id="task_2",
            type="blog",
            description="Write a blog using the research",
            depends_on=["task_1"],
        ),
        Task(
            id="task_3",
            type="email",
            description="Email the generated blog",
            depends_on=["task_2"],
            use_blog=True,
        ),
    ]

    state = {
        "tasks": tasks,
        "current_task": None,
        "completed_tasks": [],
        "running_tasks": [],
        "task_results": {},
    }

    executor = WorkflowExecutor()

    first = executor.get_next_task(
        state
    )

    assert first.id == "task_1"

    updates = executor.mark_task_running(
        state,
        "task_1",
    )

    state.update(updates)

    assert (
        state["current_task"]
        == "task_1"
    )

    updates = executor.mark_task_completed(
        state,
        "task_1",
        {
            "summary": "AI research"
        },
    )

    state.update(updates)

    second = executor.get_next_task(
        state
    )

    assert second.id == "task_2"

    updates = executor.mark_task_running(
        state,
        "task_2",
    )

    state.update(updates)

    updates = executor.mark_task_completed(
        state,
        "task_2",
        {
            "title": "AI Agents",
            "content": "Generated blog",
        },
    )

    state.update(updates)

    third = executor.get_next_task(
        state
    )

    assert third.id == "task_3"


def test_planner_executor_keeps_independent_tasks_independent():
    tasks = [
        Task(
            id="task_1",
            type="research",
            description="Research AI",
        ),
        Task(
            id="task_2",
            type="email",
            description="Send independent email",
        ),
    ]

    state = {
        "tasks": tasks,
        "completed_tasks": [],
        "running_tasks": [],
    }

    scheduler = TaskScheduler()

    ready = scheduler.get_ready_tasks(
        state
    )

    assert [
        task.id
        for task in ready
    ] == [
        "task_1",
        "task_2",
    ]