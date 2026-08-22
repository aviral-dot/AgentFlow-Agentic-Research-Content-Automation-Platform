import pytest
from pydantic import ValidationError

from src.nodes.supervisor_node import (
    SupervisorDecision,
    SupervisorNode,
)


@pytest.mark.asyncio
async def test_supervisor_routes_blog_request(fake_llm):
    node = SupervisorNode(fake_llm)

    node.structured_llm.result = SupervisorDecision(
        route="blog"
    )

    state = {
        "query": "Write a blog about AI"
    }

    result = await node.decide(state)

    assert result["route"] == "blog"


@pytest.mark.asyncio
async def test_supervisor_routes_email_request(fake_llm):
    node = SupervisorNode(fake_llm)

    node.structured_llm.result = SupervisorDecision(
        route="email"
    )

    state = {
        "query": "Send an email to test@example.com"
    }

    result = await node.decide(state)

    assert result["route"] == "email"


def test_supervisor_decision_rejects_invalid_route():
    with pytest.raises(ValidationError):
        SupervisorDecision(route="invalid")