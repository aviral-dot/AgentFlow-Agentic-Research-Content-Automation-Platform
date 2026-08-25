from src.executors.task_scheduler import TaskScheduler
from src.states.blogstate import Task


def make_task(
    task_id,
    task_type="research",
    status="pending",
    depends_on=None,
):
    return Task(
        id=task_id,
        type=task_type,
        description=f"Do {task_id}",
        depends_on=depends_on or [],
        use_blog=False,
        status=status,
    )


def make_state(tasks, completed=None):
    return {
        "tasks": tasks,
        "completed_tasks": completed or [],
        "running_tasks": [],
    }


def test_task_scheduler_finds_task_by_id():
    scheduler = TaskScheduler()

    task = make_task("task_1")

    state = make_state([task])

    assert (
        scheduler.get_task_by_id(
            state,
            "task_1",
        )
        == task
    )


def test_task_scheduler_returns_none_for_unknown_task():
    scheduler = TaskScheduler()

    state = make_state(
        [make_task("task_1")]
    )

    assert (
        scheduler.get_task_by_id(
            state,
            "missing",
        )
        is None
    )


def test_task_without_dependencies_is_ready():
    scheduler = TaskScheduler()

    task = make_task("task_1")

    state = make_state([task])

    assert scheduler.dependencies_satisfied(
        task,
        state,
    )


def test_task_with_completed_dependencies_is_ready():
    scheduler = TaskScheduler()

    research = make_task(
        "task_1",
        "research",
        status="completed",
    )

    blog = make_task(
        "task_2",
        "blog",
        depends_on=["task_1"],
    )

    state = make_state(
        [research, blog],
        completed=["task_1"],
    )

    assert scheduler.dependencies_satisfied(
        blog,
        state,
    )


def test_task_with_unfinished_dependency_is_not_ready():
    scheduler = TaskScheduler()

    research = make_task(
        "task_1"
    )

    blog = make_task(
        "task_2",
        "blog",
        depends_on=["task_1"],
    )

    state = make_state(
        [research, blog]
    )

    assert not scheduler.dependencies_satisfied(
        blog,
        state,
    )


def test_get_ready_tasks_returns_independent_pending_tasks():
    scheduler = TaskScheduler()

    tasks = [
        make_task("task_1"),
        make_task("task_2"),
        make_task(
            "task_3",
            depends_on=["task_1"],
        ),
    ]

    state = make_state(tasks)

    ready = scheduler.get_ready_tasks(
        state
    )

    assert [task.id for task in ready] == [
        "task_1",
        "task_2",
    ]


def test_completed_tasks_are_not_returned_as_ready():
    scheduler = TaskScheduler()

    tasks = [
        make_task(
            "task_1",
            status="completed",
        ),
        make_task("task_2"),
    ]

    state = make_state(
        tasks,
        completed=["task_1"],
    )

    ready = scheduler.get_ready_tasks(
        state
    )

    assert [task.id for task in ready] == [
        "task_2"
    ]


def test_get_next_ready_task_returns_first_ready_task():
    scheduler = TaskScheduler()

    tasks = [
        make_task("task_1"),
        make_task("task_2"),
    ]

    state = make_state(tasks)

    result = scheduler.get_next_ready_task(
        state
    )

    assert result.id == "task_1"


def test_get_next_ready_task_returns_none_when_blocked():
    scheduler = TaskScheduler()

    tasks = [
        make_task(
            "task_1",
            depends_on=["missing"],
        )
    ]

    state = make_state(tasks)

    assert (
        scheduler.get_next_ready_task(
            state
        )
        is None
    )


def test_all_tasks_completed_for_empty_workflow():
    scheduler = TaskScheduler()

    assert scheduler.all_tasks_completed(
        {"tasks": []}
    )


def test_all_tasks_completed_accepts_terminal_states():
    scheduler = TaskScheduler()

    tasks = [
        make_task(
            "task_1",
            status="completed",
        ),
        make_task(
            "task_2",
            status="rejected",
        ),
        make_task(
            "task_3",
            status="failed",
        ),
    ]

    assert scheduler.all_tasks_completed(
        make_state(tasks)
    )


def test_running_task_prevents_completion():
    scheduler = TaskScheduler()

    state = make_state(
        [
            make_task(
                "task_1",
                status="running",
            )
        ]
    )

    assert not scheduler.all_tasks_completed(
        state
    )


def test_has_failed_task():
    scheduler = TaskScheduler()

    state = make_state(
        [
            make_task(
                "task_1",
                status="failed",
            )
        ]
    )

    assert scheduler.has_failed_task(
        state
    )


def test_has_running_task():
    scheduler = TaskScheduler()

    state = make_state(
        [
            make_task(
                "task_1",
                status="running",
            )
        ]
    )

    assert scheduler.has_running_task(
        state
    )


def test_has_pending_tasks():
    scheduler = TaskScheduler()

    state = make_state(
        [make_task("task_1")]
    )

    assert scheduler.has_pending_tasks(
        state
    )


def test_scheduler_detects_deadlock():
    scheduler = TaskScheduler()

    tasks = [
        make_task(
            "task_1",
            depends_on=["task_2"],
        ),
        make_task(
            "task_2",
            depends_on=["task_1"],
        ),
    ]

    state = make_state(tasks)

    assert scheduler.is_deadlocked(
        state
    )


def test_completed_workflow_is_not_deadlocked():
    scheduler = TaskScheduler()

    task = make_task(
        "task_1",
        status="completed",
    )

    state = make_state(
        [task],
        completed=["task_1"],
    )

    assert not scheduler.is_deadlocked(
        state
    )