from collections.abc import Iterable


def assert_task_ids(
    tasks: Iterable,
    expected_ids: list[str],
) -> None:
    actual_ids = [
        task.id
        for task in tasks
    ]

    assert actual_ids == expected_ids


def assert_task_types(
    tasks: Iterable,
    expected_types: list[str],
) -> None:
    actual_types = [
        task.type
        for task in tasks
    ]

    assert actual_types == expected_types


def assert_task_dependencies(
    tasks: Iterable,
    expected_dependencies: dict[str, list[str]],
) -> None:
    actual_dependencies = {
        task.id: list(task.depends_on)
        for task in tasks
    }

    assert actual_dependencies == expected_dependencies


def assert_task_exists(
    tasks: Iterable,
    task_id: str,
) -> None:
    task_ids = {
        task.id
        for task in tasks
    }

    assert task_id in task_ids


def assert_task_type(
    tasks: Iterable,
    task_id: str,
    expected_type: str,
) -> None:
    task = next(
        (
            task
            for task in tasks
            if task.id == task_id
        ),
        None,
    )

    assert task is not None, (
        f"Task '{task_id}' was not found."
    )

    assert task.type == expected_type


def assert_task_depends_on(
    tasks: Iterable,
    task_id: str,
    dependency_id: str,
) -> None:
    task = next(
        (
            task
            for task in tasks
            if task.id == task_id
        ),
        None,
    )

    assert task is not None, (
        f"Task '{task_id}' was not found."
    )

    assert dependency_id in task.depends_on


def assert_plan_has_task_count(
    tasks: Iterable,
    expected_count: int,
) -> None:
    actual_count = len(list(tasks))

    assert actual_count == expected_count


def assert_valid_plan(tasks: Iterable) -> None:
    """
    Validate the basic structural contract of a planner output.
    """

    tasks = list(tasks)

    assert tasks, "Planner returned an empty plan."

    task_ids = [
        task.id
        for task in tasks
    ]

    assert len(task_ids) == len(set(task_ids)), (
        "Planner returned duplicate task IDs."
    )

    task_id_set = set(task_ids)

    for task in tasks:
        assert task.id, "Every task must have an ID."
        assert task.type, (
            f"Task '{task.id}' must have a type."
        )

        assert task.description, (
            f"Task '{task.id}' must have a description."
        )

        for dependency in task.depends_on:
            assert dependency in task_id_set, (
                f"Task '{task.id}' depends on "
                f"unknown task '{dependency}'."
            )


def assert_acyclic(tasks: Iterable) -> None:
    """
    Ensure that the planner dependency graph contains no cycles.
    """

    tasks = list(tasks)

    dependencies = {
        task.id: list(task.depends_on)
        for task in tasks
    }

    visiting = set()
    visited = set()

    def visit(task_id: str) -> None:

        if task_id in visiting:
            raise AssertionError(
                f"Planner dependency graph contains a cycle "
                f"involving task '{task_id}'."
            )

        if task_id in visited:
            return

        visiting.add(task_id)

        for dependency_id in dependencies.get(task_id, []):
            visit(dependency_id)

        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)