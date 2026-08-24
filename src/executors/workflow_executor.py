from src.executors.task_scheduler import TaskScheduler
from src.states.blogstate import AgentState, Task


class WorkflowExecutor:
    """
    Manages workflow task lifecycle.

    It does NOT execute business logic.

    Lifecycle:

        pending
            ↓
        running
            ↓
        completed / rejected / failed
    """

    def __init__(self):

        self.scheduler = TaskScheduler()

    # ========================================================
    # LOOKUP
    # ========================================================

    def get_task_by_id(
        self,
        state: AgentState,
        task_id: str,
    ) -> Task | None:

        return self.scheduler.get_task_by_id(
            state,
            task_id,
        )

    def get_current_task(
        self,
        state: AgentState,
    ) -> Task | None:

        task_id = state.get(
            "current_task"
        )

        if not task_id:
            return None

        return self.get_task_by_id(
            state,
            task_id,
        )

    # ========================================================
    # SCHEDULING
    # ========================================================

    def get_ready_tasks(
        self,
        state: AgentState,
    ) -> list[Task]:

        return self.scheduler.get_ready_tasks(
            state
        )

    def get_next_task(
        self,
        state: AgentState,
    ) -> Task | None:

        return self.scheduler.get_next_ready_task(
            state
        )

    # ========================================================
    # RUNNING
    # ========================================================

    def mark_task_running(
        self,
        state: AgentState,
        task_id: str,
    ) -> dict:

        task = self.get_task_by_id(
            state,
            task_id,
        )

        if task is None:
            raise ValueError(
                f"Task '{task_id}' does not exist."
            )

        if task.status != "pending":
            raise ValueError(
                f"Task '{task_id}' cannot transition "
                f"from '{task.status}' to 'running'."
            )

        tasks = []

        for current_task in state.get(
            "tasks",
            [],
        ):

            if current_task.id == task_id:

                current_task = current_task.model_copy(
                    update={
                        "status": "running",
                    }
                )

            tasks.append(current_task)

        running_tasks = list(
            state.get(
                "running_tasks",
                [],
            )
        )

        if task_id not in running_tasks:
            running_tasks.append(task_id)

        return {
            "tasks": tasks,
            "running_tasks": running_tasks,
            "current_task": task_id,
        }

    # ========================================================
    # COMPLETED
    # ========================================================

    def mark_task_completed(
        self,
        state: AgentState,
        task_id: str,
        result,
    ) -> dict:

        task = self.get_task_by_id(
            state,
            task_id,
        )

        if task is None:
            raise ValueError(
                f"Task '{task_id}' does not exist."
            )

        if task.status != "running":
            raise ValueError(
                f"Task '{task_id}' cannot transition "
                f"from '{task.status}' to 'completed'."
            )

        tasks = []

        for current_task in state.get(
            "tasks",
            [],
        ):

            if current_task.id == task_id:

                current_task = current_task.model_copy(
                    update={
                        "status": "completed",
                        "result": result,
                    }
                )

            tasks.append(current_task)

        completed_tasks = list(
            state.get(
                "completed_tasks",
                [],
            )
        )

        if task_id not in completed_tasks:
            completed_tasks.append(task_id)

        running_tasks = [
            running_task_id
            for running_task_id in state.get(
                "running_tasks",
                [],
            )
            if running_task_id != task_id
        ]

        task_results = dict(
            state.get(
                "task_results",
                {},
            )
        )

        task_results[task_id] = result

        return {
            "tasks": tasks,
            "completed_tasks": completed_tasks,
            "running_tasks": running_tasks,
            "task_results": task_results,
            "current_task": None,
        }

    # ========================================================
    # REJECTED
    # ========================================================

    def mark_task_rejected(
        self,
        state: AgentState,
        task_id: str,
    ) -> dict:

        task = self.get_task_by_id(
            state,
            task_id,
        )

        if task is None:
            raise ValueError(
                f"Task '{task_id}' does not exist."
            )

        if task.status != "running":
            raise ValueError(
                f"Task '{task_id}' cannot be rejected "
                f"from '{task.status}'."
            )

        rejection_result = {
            "status": "rejected",
            "message": "Task rejected by human approval.",
        }

        tasks = []

        for current_task in state.get(
            "tasks",
            [],
        ):

            if current_task.id == task_id:

                current_task = current_task.model_copy(
                    update={
                        "status": "rejected",
                        "result": rejection_result,
                    }
                )

            tasks.append(current_task)

        running_tasks = [
            running_task_id
            for running_task_id in state.get(
                "running_tasks",
                [],
            )
            if running_task_id != task_id
        ]

        task_results = dict(
            state.get(
                "task_results",
                {},
            )
        )

        task_results[task_id] = rejection_result

        return {
            "tasks": tasks,
            "running_tasks": running_tasks,
            "task_results": task_results,
            "current_task": None,
        }

    # ========================================================
    # FAILED
    # ========================================================

    def mark_task_failed(
        self,
        state: AgentState,
        task_id: str,
        error: str,
    ) -> dict:

        task = self.get_task_by_id(
            state,
            task_id,
        )

        if task is None:
            raise ValueError(
                f"Task '{task_id}' does not exist."
            )

        failure_result = {
            "status": "failed",
            "error": error,
        }

        tasks = []

        for current_task in state.get(
            "tasks",
            [],
        ):

            if current_task.id == task_id:

                current_task = current_task.model_copy(
                    update={
                        "status": "failed",
                        "result": failure_result,
                    }
                )

            tasks.append(current_task)

        running_tasks = [
            running_task_id
            for running_task_id in state.get(
                "running_tasks",
                [],
            )
            if running_task_id != task_id
        ]

        task_results = dict(
            state.get(
                "task_results",
                {},
            )
        )

        task_results[task_id] = failure_result

        return {
            "tasks": tasks,
            "running_tasks": running_tasks,
            "task_results": task_results,
            "current_task": None,
        }

    # ========================================================
    # STATUS
    # ========================================================

    def is_complete(
        self,
        state: AgentState,
    ) -> bool:

        return self.scheduler.all_tasks_completed(
            state
        )

    def has_failed_task(
        self,
        state: AgentState,
    ) -> bool:

        return self.scheduler.has_failed_task(
            state
        )

    def is_deadlocked(
        self,
        state: AgentState,
    ) -> bool:

        return self.scheduler.is_deadlocked(
            state
        )