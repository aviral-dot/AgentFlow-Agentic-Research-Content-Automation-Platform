from src.states.blogstate import AgentState, Task


class TaskScheduler:
    """
    Dependency-aware task scheduler.

    The scheduler decides which tasks are ready.

    It does NOT execute tasks.
    It does NOT modify task state.
    """

    def get_task_by_id(
        self,
        state: AgentState,
        task_id: str,
    ) -> Task | None:

        for task in state.get("tasks", []):

            if task.id == task_id:
                return task

        return None

    def dependencies_satisfied(
        self,
        task: Task,
        state: AgentState,
    ) -> bool:

        dependencies = set(
            task.depends_on or []
        )

        if not dependencies:
            return True

        completed_tasks = set(
            state.get(
                "completed_tasks",
                [],
            )
        )

        return dependencies.issubset(
            completed_tasks
        )

    def get_ready_tasks(
        self,
        state: AgentState,
    ) -> list[Task]:

        ready_tasks: list[Task] = []

        for task in state.get(
            "tasks",
            [],
        ):

            if task.status != "pending":
                continue

            if self.dependencies_satisfied(
                task,
                state,
            ):
                ready_tasks.append(task)

        return ready_tasks

    def get_next_ready_task(
        self,
        state: AgentState,
    ) -> Task | None:

        ready_tasks = self.get_ready_tasks(
            state
        )

        if not ready_tasks:
            return None

        return ready_tasks[0]

    def all_tasks_completed(
        self,
        state: AgentState,
    ) -> bool:

        tasks = state.get(
            "tasks",
            [],
        )

        if not tasks:
            return True

        terminal_statuses = {
            "completed",
            "rejected",
        }

        return all(
            task.status in terminal_statuses
            for task in tasks
        )

    def has_failed_task(
        self,
        state: AgentState,
    ) -> bool:

        return any(
            task.status == "failed"
            for task in state.get(
                "tasks",
                [],
            )
        )

    def has_running_task(
        self,
        state: AgentState,
    ) -> bool:

        return any(
            task.status == "running"
            for task in state.get(
                "tasks",
                [],
            )
        )

    def has_pending_tasks(
        self,
        state: AgentState,
    ) -> bool:

        return any(
            task.status == "pending"
            for task in state.get(
                "tasks",
                [],
            )
        )

    def is_deadlocked(
        self,
        state: AgentState,
    ) -> bool:

        if self.all_tasks_completed(state):
            return False

        if self.has_failed_task(state):
            return False

        if self.has_running_task(state):
            return False

        if not self.has_pending_tasks(state):
            return False

        return not bool(
            self.get_ready_tasks(state)
        )