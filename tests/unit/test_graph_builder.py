from types import SimpleNamespace

from src.graphs import graph_builder


class FakeWorker:
    def __init__(self, llm):
        self.llm = llm

    async def research(self, state):
        return {}

    async def title_creation(self, state):
        return {}

    async def content_generation(self, state):
        return {}

    async def draft_email(self, state):
        return {}

    def approve_email(self, state):
        return {
            "approval": "approve"
        }

    async def send_email(self, state):
        return {}


class FakePlanner:
    def __init__(self, llm):
        self.llm = llm

    async def plan(self, state):
        return {}


class FakeExecutor:
    def __init__(self):
        pass

    def get_next_task(self, state):
        return None

    def get_current_task(self, state):
        return None

    def is_complete(self, state):
        return True

    def has_failed_task(self, state):
        return False

    def is_deadlocked(self, state):
        return False

    def mark_task_running(self, state, task_id):
        return {}

    def mark_task_completed(
        self,
        state,
        task_id,
        result,
    ):
        return {}

    def mark_task_rejected(
        self,
        state,
        task_id,
    ):
        return {}


def test_graph_builder_registers_expected_nodes(
    monkeypatch,
):
    monkeypatch.setattr(
        graph_builder,
        "ResearchNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "BlogNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "EmailNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "WorkflowPlanner",
        FakePlanner,
    )

    monkeypatch.setattr(
        graph_builder,
        "WorkflowExecutor",
        FakeExecutor,
    )

    builder = graph_builder.GraphBuilder(
        llm=object(),
        checkpointer=None,
    )

    graph = builder.build_graph()

    node_names = set(
        graph.nodes.keys()
    )

    expected = {
        "planner",
        "executor",
        "research",
        "title_creation",
        "content_generation",
        "draft_email",
        "approve_email",
        "send_email",
        "advance",
    }

    assert expected.issubset(
        node_names
    )


def test_graph_builder_compiles(
    monkeypatch,
):
    monkeypatch.setattr(
        graph_builder,
        "ResearchNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "BlogNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "EmailNode",
        FakeWorker,
    )

    monkeypatch.setattr(
        graph_builder,
        "WorkflowPlanner",
        FakePlanner,
    )

    monkeypatch.setattr(
        graph_builder,
        "WorkflowExecutor",
        FakeExecutor,
    )

    builder = graph_builder.GraphBuilder(
        llm=object(),
        checkpointer=None,
    )

    compiled = builder.setup_graph()

    assert compiled is not None


def test_route_after_approval():
    monkeypatch_state = None

    builder = object.__new__(
        graph_builder.GraphBuilder
    )

    assert (
        builder.route_after_approval(
            {"approval": "approve"}
        )
        == "send_email"
    )

    assert (
        builder.route_after_approval(
            {"approval": "reject"}
        )
        == "reject"
    )


def test_route_after_approval_rejects_invalid():
    builder = object.__new__(
        graph_builder.GraphBuilder
    )

    try:
        builder.route_after_approval(
            {"approval": "invalid"}
        )
    except ValueError as exc:
        assert (
            "Invalid approval decision"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )