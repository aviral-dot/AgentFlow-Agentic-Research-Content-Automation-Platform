from types import SimpleNamespace

import pytest
from langgraph.checkpoint.memory import MemorySaver


class FakeLLM:
    """
    Fake LLM used by tests.

    This class never calls a real model provider.
    """

    def __init__(self, response="fake response"):
        self.response = response

    async def ainvoke(self, prompt):
        return SimpleNamespace(
            content=self.response
        )

    def with_structured_output(self, schema, **kwargs):
        return FakeStructuredLLM(schema)


class FakeStructuredLLM:
    """
    Fake LLM for structured-output calls.

    Tests can assign the expected result through
    the `result` attribute.
    """

    def __init__(self, schema):
        self.schema = schema
        self.result = None

    async def ainvoke(self, prompt):
        return self.result


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def memory_checkpointer():
    """
    In-memory LangGraph checkpointer.

    Unit/integration tests should not require PostgreSQL.
    """

    return MemorySaver()


@pytest.fixture
def thread_config():
    """
    Standard LangGraph thread configuration.

    The same thread ID is required when testing
    interrupt/resume workflows.
    """

    return {
        "configurable": {
            "thread_id": "test-thread-001"
        }
    }


@pytest.fixture
def sample_blog_state():
    return {
        "query": "Write a blog about Generative AI"
    }


@pytest.fixture
def sample_email():
    return {
        "to": "test@example.com",
        "subject": "Meeting Tomorrow",
        "body": "This is a test email."
    }


@pytest.fixture
def sample_email_state(sample_email):
    return {
        "query": (
            "Send an email to "
            "test@example.com about tomorrow's meeting."
        ),
        "email": sample_email,
    }