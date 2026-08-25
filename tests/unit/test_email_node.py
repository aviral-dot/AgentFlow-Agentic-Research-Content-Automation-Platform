import pytest
from pydantic import ValidationError

from src.nodes.mail_node import EmailDraft, EmailNode


# ============================================================
# TEST HELPERS
# ============================================================


class FakeStructuredLLM:
    """Fake structured-output LLM used by EmailNode tests."""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.prompt = None

    def with_structured_output(self, schema, method=None):
        assert schema is EmailDraft
        assert method == "json_mode"
        return self

    async def ainvoke(self, prompt):
        self.prompt = prompt

        if self.error:
            raise self.error

        return self.result


class FakeEmailTool:
    """Fake EmailTool for testing send_email without Gmail."""

    def __init__(self, result=None):
        self.result = result
        self.calls = []

    async def send(self, *, to, subject, body):
        self.calls.append(
            {
                "to": to,
                "subject": subject,
                "body": body,
            }
        )

        return self.result or {
            "status": "success",
        }


# ============================================================
# TEST STATE
# ============================================================


class FakeTask:
    def __init__(
        self,
        task_id,
        task_type,
        description="",
        depends_on=None,
        use_blog=False,
    ):
        self.id = task_id
        self.type = task_type
        self.description = description
        self.depends_on = depends_on or []
        self.use_blog = use_blog


def make_email_task(
    task_id="email_1",
    depends_on=None,
    use_blog=True,
):
    return FakeTask(
        task_id=task_id,
        task_type="email",
        description="Send the generated blog to the recipient.",
        depends_on=depends_on or ["blog_1"],
        use_blog=use_blog,
    )


def make_blog_task(task_id="blog_1"):
    return FakeTask(
        task_id=task_id,
        task_type="blog",
        description="Generate a blog.",
    )


def make_state(
    current_task="email_1",
    tasks=None,
    task_results=None,
    email=None,
):
    return {
        "request_id": "test-request",
        "current_task": current_task,
        "tasks": tasks or [],
        "task_results": task_results or {},
        "email": email,
    }


# ============================================================
# EMAIL DRAFT MODEL
# ============================================================


def test_email_draft_accepts_valid_email():
    draft = EmailDraft(
        to="user@example.com",
        subject="Test subject",
        body="Test body",
    )

    assert str(draft.to) == "user@example.com"
    assert draft.subject == "Test subject"
    assert draft.body == "Test body"


def test_email_draft_rejects_invalid_email():
    with pytest.raises(ValidationError):
        EmailDraft(
            to="not-an-email",
            subject="Test subject",
            body="Test body",
        )


def test_email_draft_rejects_empty_subject():
    with pytest.raises(ValidationError):
        EmailDraft(
            to="user@example.com",
            subject="",
            body="Test body",
        )


def test_email_draft_rejects_empty_body():
    with pytest.raises(ValidationError):
        EmailDraft(
            to="user@example.com",
            subject="Test subject",
            body="",
        )


# ============================================================
# INITIALIZATION
# ============================================================


def test_email_node_initializes_structured_llm():
    fake_llm = FakeStructuredLLM()

    node = EmailNode(fake_llm)

    assert node.llm is fake_llm
    assert node.structured_llm is fake_llm
    assert node.email_tool is not None


# ============================================================
# GET CURRENT TASK
# ============================================================


def test_get_current_task_returns_current_email_task():
    fake_llm = FakeStructuredLLM()
    node = EmailNode(fake_llm)

    email_task = make_email_task()

    state = make_state(
        current_task="email_1",
        tasks=[email_task],
    )

    result = node.get_current_task(state)

    assert result is email_task
    assert result.id == "email_1"


def test_get_current_task_returns_none_without_current_task():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        current_task=None,
        tasks=[],
    )

    assert node.get_current_task(state) is None


def test_get_current_task_returns_none_for_unknown_task():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        current_task="email_999",
        tasks=[
            make_email_task(),
        ],
    )

    assert node.get_current_task(state) is None


# ============================================================
# GET BLOG DEPENDENCY
# ============================================================


def test_get_blog_dependency_returns_blog_result():
    node = EmailNode(FakeStructuredLLM())

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": {
                "title": "AI Agents",
                "content": "Generated blog content.",
            }
        },
    )

    result = node.get_blog_dependency(
        state,
        email_task,
    )

    assert result == {
        "title": "AI Agents",
        "content": "Generated blog content.",
    }


def test_get_blog_dependency_returns_none_when_blog_not_required():
    node = EmailNode(FakeStructuredLLM())

    email_task = make_email_task(
        depends_on=[],
        use_blog=False,
    )

    state = make_state(
        tasks=[email_task],
    )

    result = node.get_blog_dependency(
        state,
        email_task,
    )

    assert result is None


def test_get_blog_dependency_rejects_missing_blog_result():
    node = EmailNode(FakeStructuredLLM())

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={},
    )

    with pytest.raises(
        ValueError,
        match="Blog dependency 'blog_1' has no result",
    ):
        node.get_blog_dependency(
            state,
            email_task,
        )


def test_get_blog_dependency_rejects_non_dict_result():
    node = EmailNode(FakeStructuredLLM())

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": "invalid blog result",
        },
    )

    with pytest.raises(
        ValueError,
        match="Blog dependency result must be a dictionary",
    ):
        node.get_blog_dependency(
            state,
            email_task,
        )


def test_get_blog_dependency_rejects_missing_title():
    node = EmailNode(FakeStructuredLLM())

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": {
                "content": "Generated content.",
            }
        },
    )

    with pytest.raises(
        ValueError,
        match="Blog result is missing title",
    ):
        node.get_blog_dependency(
            state,
            email_task,
        )


def test_get_blog_dependency_rejects_missing_content():
    node = EmailNode(FakeStructuredLLM())

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": {
                "title": "AI Agents",
            }
        },
    )

    with pytest.raises(
        ValueError,
        match="Blog result is missing content",
    ):
        node.get_blog_dependency(
            state,
            email_task,
        )


def test_get_blog_dependency_requires_blog_dependency():
    node = EmailNode(FakeStructuredLLM())

    email_task = make_email_task(
        depends_on=[],
        use_blog=True,
    )

    state = make_state(
        tasks=[email_task],
    )

    with pytest.raises(
        ValueError,
        match="requires a blog dependency",
    ):
        node.get_blog_dependency(
            state,
            email_task,
        )


# ============================================================
# DRAFT EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_draft_email_generates_email_from_blog():
    draft = EmailDraft(
        to="user@example.com",
        subject="AI Agents",
        body="placeholder",
    )

    fake_llm = FakeStructuredLLM(
        result=draft,
    )

    node = EmailNode(fake_llm)

    blog_task = make_blog_task()

    email_task = make_email_task(
        depends_on=["blog_1"],
        use_blog=True,
    )

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": {
                "title": "AI Agents",
                "content": "This is the generated blog.",
            }
        },
    )

    result = await node.draft_email(state)

    assert result["email"]["to"] == "user@example.com"
    assert result["email"]["subject"] == "AI Agents"

    # Blog content must be used exactly as the final body.
    assert (
        result["email"]["body"]
        == "AI Agents\n\nThis is the generated blog."
    )

    assert fake_llm.prompt is not None
    assert "AI Agents" in fake_llm.prompt
    assert "This is the generated blog." in fake_llm.prompt


@pytest.mark.asyncio
async def test_draft_email_without_blog_uses_llm_body():
    draft = EmailDraft(
        to="user@example.com",
        subject="Test email",
        body="Generated email body.",
    )

    fake_llm = FakeStructuredLLM(
        result=draft,
    )

    node = EmailNode(fake_llm)

    email_task = make_email_task(
        depends_on=[],
        use_blog=False,
    )

    state = make_state(
        tasks=[email_task],
    )

    result = await node.draft_email(state)

    assert result["email"] == {
        "to": "user@example.com",
        "subject": "Test email",
        "body": "Generated email body.",
    }


@pytest.mark.asyncio
async def test_draft_email_requires_current_task():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        current_task=None,
    )

    with pytest.raises(
        ValueError,
        match="No current email task exists",
    ):
        await node.draft_email(state)


@pytest.mark.asyncio
async def test_draft_email_rejects_non_email_task():
    node = EmailNode(FakeStructuredLLM())

    non_email_task = FakeTask(
        task_id="blog_1",
        task_type="blog",
    )

    state = make_state(
        current_task="blog_1",
        tasks=[non_email_task],
    )

    with pytest.raises(
        ValueError,
        match="Current task is not an email task",
    ):
        await node.draft_email(state)


@pytest.mark.asyncio
async def test_draft_email_propagates_llm_error():
    fake_llm = FakeStructuredLLM(
        error=RuntimeError("LLM failure"),
    )

    node = EmailNode(fake_llm)

    blog_task = make_blog_task()

    email_task = make_email_task()

    state = make_state(
        tasks=[
            blog_task,
            email_task,
        ],
        task_results={
            "blog_1": {
                "title": "AI Agents",
                "content": "Blog content",
            }
        },
    )

    with pytest.raises(
        RuntimeError,
        match="LLM failure",
    ):
        await node.draft_email(state)


# ============================================================
# APPROVAL
# ============================================================


def test_approve_email_rejects_missing_email():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        email=None,
    )

    with pytest.raises(
        ValueError,
        match="Email draft is missing",
    ):
        node.approve_email(state)


def test_approve_email_returns_approval_decision(
    monkeypatch,
):
    node = EmailNode(FakeStructuredLLM())

    email = {
        "to": "user@example.com",
        "subject": "Test",
        "body": "Test body",
    }

    email_task = make_email_task()

    state = make_state(
        current_task="email_1",
        tasks=[email_task],
        email=email,
    )

    monkeypatch.setattr(
        "src.nodes.mail_node.interrupt",
        lambda payload: {
            "decision": "approve",
        },
    )

    result = node.approve_email(state)

    assert result == {
        "approval": "approve",
    }


def test_approve_email_accepts_approval_key(
    monkeypatch,
):
    node = EmailNode(FakeStructuredLLM())

    email = {
        "to": "user@example.com",
        "subject": "Test",
        "body": "Test body",
    }

    email_task = make_email_task()

    state = make_state(
        current_task="email_1",
        tasks=[email_task],
        email=email,
    )

    monkeypatch.setattr(
        "src.nodes.mail_node.interrupt",
        lambda payload: {
            "approval": "reject",
        },
    )

    result = node.approve_email(state)

    assert result == {
        "approval": "reject",
    }


def test_approve_email_rejects_invalid_decision(
    monkeypatch,
):
    node = EmailNode(FakeStructuredLLM())

    email = {
        "to": "user@example.com",
        "subject": "Test",
        "body": "Test body",
    }

    email_task = make_email_task()

    state = make_state(
        current_task="email_1",
        tasks=[email_task],
        email=email,
    )

    monkeypatch.setattr(
        "src.nodes.mail_node.interrupt",
        lambda payload: {
            "decision": "maybe",
        },
    )

    with pytest.raises(
        ValueError,
        match="Invalid approval decision",
    ):
        node.approve_email(state)


def test_approve_email_sends_correct_interrupt_payload(
    monkeypatch,
):
    node = EmailNode(FakeStructuredLLM())

    email = {
        "to": "user@example.com",
        "subject": "Test",
        "body": "Test body",
    }

    email_task = make_email_task()

    state = make_state(
        current_task="email_1",
        tasks=[email_task],
        email=email,
    )

    captured_payload = {}

    def fake_interrupt(payload):
        captured_payload.update(payload)
        return "approve"

    monkeypatch.setattr(
        "src.nodes.mail_node.interrupt",
        fake_interrupt,
    )

    result = node.approve_email(state)

    assert result == {
        "approval": "approve",
    }

    assert captured_payload == {
        "type": "email_approval",
        "task_id": "email_1",
        "message": (
            "Please approve or reject "
            "this email before sending."
        ),
        "email": email,
    }


# ============================================================
# SEND EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_send_email_sends_valid_email():
    node = EmailNode(FakeStructuredLLM())

    fake_tool = FakeEmailTool(
        result={
            "message_id": "test-message-id",
        }
    )

    node.email_tool = fake_tool

    email = {
        "to": "user@example.com",
        "subject": "Test subject",
        "body": "Test body",
    }

    state = make_state(
        email=email,
    )

    result = await node.send_email(state)

    assert result["response"] == "Email Sent Successfully"

    assert result["email"] == email

    assert result["tool_result"] == {
        "message_id": "test-message-id",
    }

    assert result["task_result"]["status"] == "sent"
    assert (
        result["task_result"]["message"]
        == "Email Sent Successfully"
    )

    assert fake_tool.calls == [
        {
            "to": "user@example.com",
            "subject": "Test subject",
            "body": "Test body",
        }
    ]


@pytest.mark.asyncio
async def test_send_email_rejects_missing_email():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        email=None,
    )

    with pytest.raises(
        ValueError,
        match="Email draft is missing",
    ):
        await node.send_email(state)


@pytest.mark.asyncio
async def test_send_email_rejects_invalid_email():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        email={
            "to": "invalid-email",
            "subject": "Test",
            "body": "Test body",
        },
    )

    with pytest.raises(ValidationError):
        await node.send_email(state)


@pytest.mark.asyncio
async def test_send_email_rejects_empty_subject():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        email={
            "to": "user@example.com",
            "subject": "",
            "body": "Test body",
        },
    )

    with pytest.raises(ValidationError):
        await node.send_email(state)


@pytest.mark.asyncio
async def test_send_email_rejects_empty_body():
    node = EmailNode(FakeStructuredLLM())

    state = make_state(
        email={
            "to": "user@example.com",
            "subject": "Test",
            "body": "",
        },
    )

    with pytest.raises(ValidationError):
        await node.send_email(state)