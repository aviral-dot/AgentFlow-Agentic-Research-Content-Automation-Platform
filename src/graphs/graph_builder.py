# import logging

# from langgraph.graph import END, START, StateGraph

# from src.nodes.blog_node import BlogNode
# from src.nodes.mail_node import EmailNode
# from src.nodes.supervisor_node import SupervisorNode
# from src.states.blogstate import AgentState
# from src.utils.loggers import (
#     get_logger,
#     log_event,
# )


# logger = get_logger(__name__)


# class GraphBuilder:

#     def __init__(
#         self,
#         llm,
#         checkpointer,
#     ):

#         self.llm = llm
#         self.checkpointer = checkpointer

#         self.graph = StateGraph(
#             AgentState
#         )

#         self.blog_node = BlogNode(
#             self.llm
#         )

#         self.email_node = EmailNode(
#             self.llm
#         )

#         self.supervisor_node = SupervisorNode(
#             self.llm
#         )

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_builder_initialized",
#         )

#     # ========================================================
#     # BUILD GRAPH
#     # ========================================================

#     def build_graph(self):

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_build_started",
#         )

#         # ----------------------------------------------------
#         # NODES
#         # ----------------------------------------------------

#         self.graph.add_node(
#             "supervisor",
#             self.supervisor_node.decide,
#         )

#         self.graph.add_node(
#             "title_creation",
#             self.blog_node.title_creation,
#         )

#         self.graph.add_node(
#             "content_generation",
#             self.blog_node.content_generation,
#         )

#         self.graph.add_node(
#             "draft_email",
#             self.email_node.draft_email,
#         )

#         self.graph.add_node(
#             "approve_email",
#             self.email_node.approve_email,
#         )

#         self.graph.add_node(
#             "send_email",
#             self.email_node.send_email,
#         )

#         # ----------------------------------------------------
#         # START → SUPERVISOR
#         # ----------------------------------------------------

#         self.graph.add_edge(
#             START,
#             "supervisor",
#         )

#         # ----------------------------------------------------
#         # SUPERVISOR → BLOG / EMAIL
#         # ----------------------------------------------------

#         self.graph.add_conditional_edges(
#             "supervisor",
#             self.route_request,
#             {
#                 "blog": "title_creation",
#                 "email": "draft_email",
#             },
#         )

#         # ----------------------------------------------------
#         # BLOG WORKFLOW
#         # ----------------------------------------------------

#         self.graph.add_edge(
#             "title_creation",
#             "content_generation",
#         )

#         self.graph.add_edge(
#             "content_generation",
#             END,
#         )

#         # ----------------------------------------------------
#         # EMAIL WORKFLOW
#         # ----------------------------------------------------

#         self.graph.add_edge(
#             "draft_email",
#             "approve_email",
#         )

#         self.graph.add_conditional_edges(
#             "approve_email",
#             self.route_after_approval,
#             {
#                 "send_email": "send_email",
#                 "end": END,
#             },
#         )

#         self.graph.add_edge(
#             "send_email",
#             END,
#         )

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_build_completed",
#             nodes=[
#                 "supervisor",
#                 "title_creation",
#                 "content_generation",
#                 "draft_email",
#                 "approve_email",
#                 "send_email",
#             ],
#             status="success",
#         )

#         return self.graph

#     # ========================================================
#     # ROUTING
#     # ========================================================

#     def route_request(
#         self,
#         state: AgentState,
#     ):

#         route = state["route"]

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_route_selected",
#             route=route,
#         )

#         return route

#     def route_after_approval(
#         self,
#         state: AgentState,
#     ):

#         approval = state["approval"]

#         if approval == "approve":

#             log_event(
#                 logger,
#                 level=logging.INFO,
#                 event="email_approval_route_selected",
#                 decision="approve",
#                 next_node="send_email",
#             )

#             return "send_email"

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="email_approval_route_selected",
#             decision="reject",
#             next_node="end",
#         )

#         return "end"

#     # ========================================================
#     # GRAPH COMPILATION
#     # ========================================================

#     def setup_graph(self):

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_compilation_started",
#         )

#         try:

#             graph = self.build_graph()

#             compiled_graph = graph.compile(
#                 checkpointer=self.checkpointer
#             )

#         except Exception:

#             logger.exception(
#                 "Graph compilation failed",
#                 extra={
#                     "event": "graph_compilation_failed",
#                     "context": {},
#                 },
#             )

#             raise

#         log_event(
#             logger,
#             level=logging.INFO,
#             event="graph_compilation_completed",
#             status="success",
#         )

#         return compiled_graph


import logging

from langgraph.graph import END, START, StateGraph

from src.executors.workflow_executor import (
    WorkflowExecutor,
)
from src.nodes.blog_node import BlogNode
from src.nodes.mail_node import EmailNode
from src.planners.workflow_planner import (
    WorkflowPlanner,
)
from src.states.blogstate import AgentState
from src.utils.loggers import (
    get_logger,
    log_event,
)


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

        # ----------------------------------------------------
        # EXISTING NODES
        # ----------------------------------------------------

        self.blog_node = BlogNode(
            self.llm
        )

        self.email_node = EmailNode(
            self.llm
        )

        # ----------------------------------------------------
        # NEW PLANNER
        # ----------------------------------------------------

        self.planner = WorkflowPlanner(
            self.llm
        )

        # ----------------------------------------------------
        # NEW EXECUTOR
        # ----------------------------------------------------

        self.executor = WorkflowExecutor()

        log_event(
            logger,
            level=logging.INFO,
            event="graph_builder_initialized",
        )

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    def build_graph(self):

        log_event(
            logger,
            level=logging.INFO,
            event="graph_build_started",
        )

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
        # BLOG NODES
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
        # EMAIL NODES
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
        # ADVANCE NODE
        # ----------------------------------------------------

        self.graph.add_node(
            "advance",
            self.executor.advance,
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
        # EXECUTOR → NEXT TASK
        # ====================================================

        self.graph.add_conditional_edges(
            "executor",
            self.route_task,
            {
                "blog": "title_creation",
                "email": "draft_email",
                "end": END,
            },
        )

        # ====================================================
        # BLOG WORKFLOW
        # ====================================================

        self.graph.add_edge(
            "title_creation",
            "content_generation",
        )

        self.graph.add_edge(
            "content_generation",
            "advance",
        )

        # ====================================================
        # EMAIL WORKFLOW
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
                "end": END,
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

        # ====================================================
        # LOG GRAPH
        # ====================================================

        log_event(
            logger,
            level=logging.INFO,
            event="graph_build_completed",
            nodes=[
                "planner",
                "executor",
                "title_creation",
                "content_generation",
                "draft_email",
                "approve_email",
                "send_email",
                "advance",
            ],
            status="success",
        )

        return self.graph

    # ========================================================
    # EXECUTOR NODE
    # ========================================================

    def executor_node(
        self,
        state: AgentState,
    ):

        task = self.executor.get_current_task(
            state
        )

        if task is None:

            log_event(
                logger,
                level=logging.INFO,
                event="workflow_execution_completed",
            )

            return {}

        log_event(
            logger,
            level=logging.INFO,
            event="workflow_task_selected",
            task_id=task.id,
            task_type=task.type,
            current_task=state.get(
                "current_task",
                0,
            ),
        )

        return {}

    # ========================================================
    # TASK ROUTING
    # ========================================================

    def route_task(
        self,
        state: AgentState,
    ):

        task_type = (
            self.executor.get_next_task_type(
                state
            )
        )

        log_event(
            logger,
            level=logging.INFO,
            event="workflow_task_routed",
            task_type=task_type,
            current_task=state.get(
                "current_task",
                0,
            ),
        )

        return task_type

    # ========================================================
    # EMAIL APPROVAL ROUTING
    # ========================================================

    def route_after_approval(
        self,
        state: AgentState,
    ):

        approval = state["approval"]

        if approval == "approve":

            log_event(
                logger,
                level=logging.INFO,
                event="email_approval_route_selected",
                decision="approve",
                next_node="send_email",
            )

            return "send_email"

        log_event(
            logger,
            level=logging.INFO,
            event="email_approval_route_selected",
            decision="reject",
            next_node="end",
        )

        return "end"

    # ========================================================
    # GRAPH COMPILATION
    # ========================================================

    def setup_graph(self):

        log_event(
            logger,
            level=logging.INFO,
            event="graph_compilation_started",
        )

        try:

            graph = self.build_graph()

            compiled_graph = graph.compile(
                checkpointer=self.checkpointer
            )

        except Exception:

            logger.exception(
                "Graph compilation failed",
                extra={
                    "event": "graph_compilation_failed",
                    "context": {},
                },
            )

            raise

        log_event(
            logger,
            level=logging.INFO,
            event="graph_compilation_completed",
            status="success",
        )

        return compiled_graph