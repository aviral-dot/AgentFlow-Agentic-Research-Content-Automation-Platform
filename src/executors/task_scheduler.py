from src.states.blogstate import AgentState, Task


class TaskScheduler:
    """
    Dependency-aware workflow scheduler.

    Responsibilities:
        - Find tasks that are ready to execute.
        - Check task dependencies.
        - Detect workflow completion.
        - Detect failures.
        - Detect deadlocks.

    The scheduler does NOT:
        - Execute business logic.
        - Call LLMs.
        - Call Tavily.
        - Send emails.
        - Generate blogs.
        - Modify task state.
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
        """
        Return True when every dependency of the task
        has completed successfully.

        Example:

            task_1 = research
            task_2 = blog depends on task_1

        task_2 becomes ready only after task_1
        appears in completed_tasks.
        """

        dependencies = set(
            task.depends_on or []
        )

        # No dependencies means the task is immediately ready.
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
        """
        Return all pending tasks whose dependencies
        have been satisfied.

        This supports independent parallel workflows.

        Example:

            task_1 = research
            task_2 = email

        Both can be returned as ready if neither
        depends on the other.
        """

        ready_tasks: list[Task] = []

        for task in state.get(
            "tasks",
            [],
        ):

            # Only pending tasks can become ready.
            if task.status != "pending":
                continue

            # Dependency check.
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
        """
        Return the first ready task.

        The executor decides how this task is executed.
        """

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
        """
        Return True when every task has reached
        a terminal state.

        Terminal states:

            completed
            rejected
            failed
        """

        tasks = state.get(
            "tasks",
            [],
        )

        if not tasks:
            return True

        terminal_statuses = {
            "completed",
            "rejected",
            "failed",
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
        """
        Detect a workflow where:

            - workflow is not complete
            - no task has failed
            - no task is running
            - pending tasks exist
            - but no pending task is ready

        Example:

            task_1 depends on task_2
            task_2 depends on task_1

        The planner should prevent this through cycle
        validation, but the scheduler still protects
        the runtime.
        """

        # Already finished.
        if self.all_tasks_completed(
            state
        ):
            return False

        # Failure already exists.
        if self.has_failed_task(
            state
        ):
            return False

        # Something is currently executing.
        if self.has_running_task(
            state
        ):
            return False

        # Nothing is pending.
        if not self.has_pending_tasks(
            state
        ):
            return False

        # Pending tasks exist but none are executable.
        return not bool(
            self.get_ready_tasks(
                state
            )
        )