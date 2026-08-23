from src.states.blogstate import AgentState


class WorkflowExecutor:
    """
    Controls which planned task should execute next.

    The executor does not perform business logic.
    It only manages workflow progression.
    """

    def get_current_task(
        self,
        state: AgentState,
    ):

        tasks = state.get(
            "tasks",
            [],
        )

        current_task = state.get(
            "current_task",
            0,
        )

        if current_task >= len(tasks):
            return None

        return tasks[current_task]

    def get_next_task_type(
        self,
        state: AgentState,
    ):

        task = self.get_current_task(
            state
        )

        if task is None:
            return "end"

        return task.type

    def advance(
        self,
        state: AgentState,
    ):

        current_task = state.get(
            "current_task",
            0,
        )

        tasks = state.get(
            "tasks",
            [],
        )

        completed_tasks = list(
            state.get(
                "completed_tasks",
                [],
            )
        )

        if current_task < len(tasks):

            task = tasks[current_task]

            completed_tasks.append(
                task.type
            )

        return {
            "current_task": current_task + 1,
            "completed_tasks": completed_tasks,
        }