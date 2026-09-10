import logging

from langgraph.graph import END, START, StateGraph

from src.errors.exceptions import (
    AgentFlowError,
    ExecutorFailure,
    InvalidWorkflowError,
    WorkflowDeadlockError,
)

from src.executors.workflow_executor import WorkflowExecutor
from src.nodes.blog_node import BlogNode
from src.nodes.mail_node import EmailNode
from src.nodes.research_node import ResearchNode
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

        # ====================================================
        # WORKER NODES
        # ====================================================

        self.research_node = ResearchNode(
            llm
        )

        self.blog_node = BlogNode(
            llm
        )

        self.email_node = EmailNode(
            llm
        )

        # ====================================================
        # PLANNER / EXECUTOR
        # ====================================================

        self.planner = WorkflowPlanner(
            llm
        )

        self.executor = WorkflowExecutor()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_builder_initialized",
            architecture="planner_executor",
            workers=[
                "research",
                "blog",
                "email",
            ],
        )

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    def build_graph(self):

        # ====================================================
        # PLANNER
        # ====================================================

        self.graph.add_node(
            "planner",
            self.planner.plan,
        )

        # ====================================================
        # EXECUTOR
        # ====================================================

        self.graph.add_node(
            "executor",
            self.executor_node,
        )

        # ====================================================
        # RESEARCH
        # ====================================================

        self.graph.add_node(
            "research",
            self.research_node.research,
        )

        # ====================================================
        # BLOG
        #
        # ONE node now performs:
        #
        #   title generation
        #   content generation
        #
        # using ONE LLM call.
        # ====================================================

        self.graph.add_node(
            "generate_blog",
            self.blog_node.generate_blog,
        )

        # ====================================================
        # EMAIL
        # ====================================================

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

        # ====================================================
        # ADVANCE
        # ====================================================

        self.graph.add_node(
            "advance",
            self.advance_node,
        )

        # ====================================================
        # START → PLANNER
        # ====================================================

        self.graph.add_edge(
            START,
            "planner",
        )

        # ====================================================
        # PLANNER → EXECUTOR
        # ====================================================

        self.graph.add_edge(
            "planner",
            "executor",
        )

        # ====================================================
        # EXECUTOR → WORKER
        # ====================================================

        self.graph.add_conditional_edges(
            "executor",
            self.route_task,
            {
                "research": "research",
                "blog": "generate_blog",
                "email": "draft_email",
                "end": END,
            },
        )

        # ====================================================
        # RESEARCH
        # ====================================================

        self.graph.add_edge(
            "research",
            "advance",
        )

        # ====================================================
        # BLOG
        #
        # ONE BLOG NODE
        # generate_blog() returns:
        #
        # {
        #     "blog": {
        #         "title": "...",
        #         "content": "..."
        #     },
        #     "task_result": {
        #         "title": "...",
        #         "content": "..."
        #     }
        # }
        # ====================================================

        self.graph.add_edge(
            "generate_blog",
            "advance",
        )

        # ====================================================
        # EMAIL
        # ====================================================

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

        # ====================================================
        # ADVANCE → EXECUTOR
        # ====================================================

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

        # ====================================================
        # NO READY TASK
        # ====================================================

        if task is None:

            # ------------------------------------------------
            # COMPLETE
            # ------------------------------------------------

            if self.executor.is_complete(
                state
            ):

                workflow_results = (
                    self.build_workflow_output(
                        state
                    )
                )

                return {
                    "current_task": None,
                    "workflow_results": workflow_results,
                    "response": (
                        "Workflow completed successfully."
                    ),
                }

            # ------------------------------------------------
            # FAILED
            # ------------------------------------------------

            if self.executor.has_failed_task(
                state
            ):

                workflow_results = (
                    self.build_workflow_output(
                        state
                    )
                )

                return {
                    "current_task": None,
                    "workflow_results": workflow_results,
                    "response": (
                        "Workflow failed."
                    ),
                }

            # ------------------------------------------------
            # DEADLOCK
            # ------------------------------------------------

            if self.executor.is_deadlocked(
                state
            ):

                logger.error(
                  "Workflow deadlock detected",
                    extra={
                     "event": "workflow_deadlock_detected",
                    },
                )

                raise WorkflowDeadlockError(
                    context={
                     "operation": "executor_node",
                    },
                )
        # ====================================================
        # SELECT NEXT READY TASK
        # ====================================================

        log_event(
            logger,
            level=logging.INFO,
            event="workflow_task_selected",
            task_id=task.id,
            task_type=task.type,
            depends_on=task.depends_on,
        )

        try:
           return self.executor.mark_task_running(
             state,
             task.id,
           )

        except AgentFlowError:
            raise

        except Exception as exc:
                logger.exception(
                    "Workflow executor failed",
                    extra={
                        "event": "workflow_executor_failed",
                        "task_id": task.id,
                        "task_type": task.type,
                         },
                )

                raise ExecutorFailure(
                    context={
                        "operation": "mark_task_running",
                        "task_id": task.id,
                    },
                ) from exc

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

        # ----------------------------------------------------
        # NO CURRENT TASK
        # ----------------------------------------------------

        if task is None:
            return "end"

        # ----------------------------------------------------
        # RESEARCH
        # ----------------------------------------------------

        if task.type == "research":

            return "research"

        # ----------------------------------------------------
        # BLOG
        # ----------------------------------------------------

        if task.type == "blog":

            return "blog"

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        if task.type == "email":

            return "email"

        raise InvalidWorkflowError(
            context={
        "operation": "route_task",
        "reason": "unsupported_task_type",
        "task_type": task.type,
    },
)

    # ========================================================
    # ADVANCE NODE
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

        # ====================================================
        # REJECTED EMAIL
        # ====================================================

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

            updated_state.update(
                updates
            )

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

            log_event(
                logger,
                level=logging.INFO,
                event="workflow_task_rejected",
                task_id=task.id,
                task_type=task.type,
            )

            return updates

        # ====================================================
        # NORMAL COMPLETION
        # ====================================================

        result = state.get(
            "task_result"
        )

        if result is None:

            raise RuntimeError(
                f"Task '{task.id}' finished worker "
                "execution without producing "
                "task_result."
            )

        updates = (
            self.executor.mark_task_completed(
                state,
                task.id,
                result,
            )
        )

        updated_state = dict(state)

        updated_state.update(
            updates
        )

        updates["workflow_results"] = (
            self.build_workflow_output(
                updated_state
            )
        )

        # ====================================================
        # CLEAR TRANSIENT STATE
        # ====================================================

        updates.update(
            {
                "task_result": None,
                "approval": None,
                "current_task": None,
            }
        )

        # ----------------------------------------------------
        # Keep worker artifacts because downstream tasks
        # may need them.
        # ----------------------------------------------------

        log_event(
            logger,
            level=logging.INFO,
            event="workflow_task_completed",
            task_id=task.id,
            task_type=task.type,
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

        raise InvalidWorkflowError(
    context={
        "operation": "route_after_approval",
        "reason": "invalid_approval_decision",
    },
)

    # ========================================================
    # BUILD WORKFLOW OUTPUT
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