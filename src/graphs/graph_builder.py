import logging

from langgraph.graph import END, START, StateGraph

from src.executors.workflow_executor import WorkflowExecutor
from src.nodes.blog_node import BlogNode
from src.nodes.mail_node import EmailNode
from src.planners.workflow_planner import WorkflowPlanner
from src.states.blogstate import AgentState
from src.utils.loggers import get_logger, log_event


logger = get_logger(__name__)


class GraphBuilder:

    def __init__(
        self,
        llm,
        checkpointer,
    ):

        self.llm = llm
        self.checkpointer = checkpointer

        self.graph = StateGraph(
            AgentState
        )

        self.blog_node = BlogNode(
            llm
        )

        self.email_node = EmailNode(
            llm
        )

        self.planner = WorkflowPlanner(
            llm
        )

        self.executor = WorkflowExecutor()

    # ========================================================
    # BUILD
    # ========================================================

    def build_graph(self):

        # ----------------------------------------------------
        # PLANNER
        # ----------------------------------------------------

        self.graph.add_node(
            "planner",
            self.planner.plan,
        )

        # ----------------------------------------------------
        # EXECUTOR
        # ----------------------------------------------------

        self.graph.add_node(
            "executor",
            self.executor_node,
        )

        # ----------------------------------------------------
        # BLOG
        # ----------------------------------------------------

        self.graph.add_node(
            "title_creation",
            self.blog_node.title_creation,
        )

        self.graph.add_node(
            "content_generation",
            self.blog_node.content_generation,
        )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        self.graph.add_node(
            "draft_email",
            self.email_node.draft_email,
        )

        self.graph.add_node(
            "approve_email",
            self.email_node.approve_email,
        )

        self.graph.add_node(
            "send_email",
            self.email_node.send_email,
        )

        # ----------------------------------------------------
        # ADVANCE
        # ----------------------------------------------------

        self.graph.add_node(
            "advance",
            self.advance_node,
        )

        # ====================================================
        # GRAPH EDGES
        # ====================================================

        self.graph.add_edge(
            START,
            "planner",
        )

        self.graph.add_edge(
            "planner",
            "executor",
        )

        # ----------------------------------------------------
        # EXECUTOR → WORKER
        # ----------------------------------------------------

        self.graph.add_conditional_edges(
            "executor",
            self.route_task,
            {
                "blog": "title_creation",
                "email": "draft_email",
                "end": END,
            },
        )

        # ----------------------------------------------------
        # BLOG
        # ----------------------------------------------------

        self.graph.add_edge(
            "title_creation",
            "content_generation",
        )

        self.graph.add_edge(
            "content_generation",
            "advance",
        )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        self.graph.add_edge(
            "draft_email",
            "approve_email",
        )

        self.graph.add_conditional_edges(
            "approve_email",
            self.route_after_approval,
            {
                "send_email": "send_email",
                "reject": "advance",
            },
        )

        self.graph.add_edge(
            "send_email",
            "advance",
        )

        # ----------------------------------------------------
        # ADVANCE → EXECUTOR
        # ----------------------------------------------------

        self.graph.add_edge(
            "advance",
            "executor",
        )

        return self.graph

    # ========================================================
    # EXECUTOR NODE
    # ========================================================

    def executor_node(
        self,
        state: AgentState,
    ):

        task = self.executor.get_next_task(
            state
        )

        # ----------------------------------------------------
        # NO READY TASK
        # ----------------------------------------------------

        if task is None:

            if self.executor.is_complete(
                state
            ):

                return {
                    "current_task": None,
                    "workflow_results": (
                        self.build_workflow_output(
                            state
                        )
                    ),
                    "response": (
                        "Workflow completed successfully."
                    ),
                }

            if self.executor.has_failed_task(
                state
            ):

                return {
                    "current_task": None,
                    "workflow_results": (
                        self.build_workflow_output(
                            state
                        )
                    ),
                    "response": (
                        "Workflow failed."
                    ),
                }

            if self.executor.is_deadlocked(
                state
            ):

                raise RuntimeError(
                    "Workflow is deadlocked."
                )

            return {
                "current_task": None,
            }

        # ----------------------------------------------------
        # SELECT TASK
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.INFO,
            event="workflow_task_selected",
            task_id=task.id,
            task_type=task.type,
            depends_on=task.depends_on,
        )

        return self.executor.mark_task_running(
            state,
            task.id,
        )

    # ========================================================
    # ROUTE TASK
    # ========================================================

    def route_task(
        self,
        state: AgentState,
    ):

        task = self.executor.get_current_task(
            state
        )

        if task is None:
            return "end"

        if task.type == "blog":
            return "blog"

        if task.type == "email":
            return "email"

        raise ValueError(
            f"Unsupported task type: {task.type}"
        )

    # ========================================================
    # ADVANCE
    # ========================================================

    def advance_node(
        self,
        state: AgentState,
    ):

        task = self.executor.get_current_task(
            state
        )

        if task is None:
            return {}

        # ----------------------------------------------------
        # REJECTED EMAIL
        # ----------------------------------------------------

        if (
            task.type == "email"
            and state.get("approval") == "reject"
        ):

            updates = (
                self.executor.mark_task_rejected(
                    state,
                    task.id,
                )
            )

            updated_state = dict(state)
            updated_state.update(updates)

            updates["workflow_results"] = (
                self.build_workflow_output(
                    updated_state
                )
            )

            updates.update(
                {
                    "approval": None,
                    "task_result": None,
                    "email": None,
                }
            )

            return updates

        # ----------------------------------------------------
        # NORMAL COMPLETION
        # ----------------------------------------------------

        result = state.get(
            "task_result"
        )

        if result is None:

            raise RuntimeError(
                f"Task '{task.id}' finished worker execution "
                "without producing task_result."
            )

        updates = (
            self.executor.mark_task_completed(
                state,
                task.id,
                result,
            )
        )

        updated_state = dict(state)
        updated_state.update(updates)

        updates["workflow_results"] = (
            self.build_workflow_output(
                updated_state
            )
        )

        updates.update(
            {
                "task_result": None,
                "approval": None,
            }
        )

        return updates

    # ========================================================
    # APPROVAL ROUTING
    # ========================================================

    def route_after_approval(
        self,
        state: AgentState,
    ):

        approval = state.get(
            "approval"
        )

        if approval == "approve":
            return "send_email"

        if approval == "reject":
            return "reject"

        raise ValueError(
            "Invalid approval decision."
        )

    # ========================================================
    # OUTPUT
    # ========================================================

    def build_workflow_output(
        self,
        state: AgentState,
    ) -> list[dict]:

        results = []

        task_results = state.get(
            "task_results",
            {},
        )

        for task in state.get(
            "tasks",
            [],
        ):

            if task.status not in {
                "completed",
                "rejected",
                "failed",
            }:
                continue

            results.append(
                {
                    "task_id": task.id,
                    "task_type": task.type,
                    "status": task.status,
                    "result": task_results.get(
                        task.id
                    ),
                }
            )

        return results

    # ========================================================
    # COMPILE
    # ========================================================

    def setup_graph(self):

        graph = self.build_graph()

        return graph.compile(
            checkpointer=self.checkpointer
        )