import pytest

from src.tools.research_tool import ResearchTool


class FakeTavilyClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def search(self, **kwargs):
        self.calls.append(kwargs)

        if self.error:
            raise self.error

        return self.response


@pytest.mark.asyncio
async def test_research_tool_normalizes_tavily_response(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    fake_client = FakeTavilyClient(
        response={
            "answer": "Test answer",
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "content": "Content 1",
                    "score": 0.91,
                },
                {
                    "title": "Result 2",
                    "url": "https://example.com/2",
                    "content": "Content 2",
                    "score": 0.82,
                },
            ],
        }
    )

    monkeypatch.setattr(
        "src.tools.research_tool.AsyncTavilyClient",
        lambda api_key: fake_client,
    )

    tool = ResearchTool()

    result = await tool.search(
        query="latest AI developments",
        max_results=2,
    )

    assert result["query"] == "latest AI developments"
    assert result["answer"] == "Test answer"
    assert len(result["sources"]) == 2

    assert result["sources"][0] == {
        "title": "Result 1",
        "url": "https://example.com/1",
        "content": "Content 1",
        "score": 0.91,
    }

    assert fake_client.calls == [
        {
            "query": "latest AI developments",
            "search_depth": "advanced",
            "max_results": 2,
            "include_answer": True,
            "include_raw_content": False,
        }
    ]


@pytest.mark.asyncio
async def test_research_tool_strips_query(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    fake_client = FakeTavilyClient(
        response={
            "answer": "",
            "results": [],
        }
    )

    monkeypatch.setattr(
        "src.tools.research_tool.AsyncTavilyClient",
        lambda api_key: fake_client,
    )

    tool = ResearchTool()

    result = await tool.search(
        query="  AI agents  ",
    )

    assert result["query"] == "AI agents"
    assert fake_client.calls[0]["query"] == "AI agents"


@pytest.mark.asyncio
async def test_research_tool_rejects_empty_query(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    monkeypatch.setattr(
        "src.tools.research_tool.AsyncTavilyClient",
        lambda api_key: FakeTavilyClient(),
    )

    tool = ResearchTool()

    with pytest.raises(
        ValueError,
        match="Research query cannot be empty",
    ):
        await tool.search("   ")


@pytest.mark.asyncio
async def test_research_tool_rejects_invalid_max_results(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    monkeypatch.setattr(
        "src.tools.research_tool.AsyncTavilyClient",
        lambda api_key: FakeTavilyClient(),
    )

    tool = ResearchTool()

    with pytest.raises(
        ValueError,
        match="max_results must be greater than zero",
    ):
        await tool.search(
            "AI agents",
            max_results=0,
        )


def test_research_tool_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "TAVILY_API_KEY",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="TAVILY_API_KEY",
    ):
        ResearchTool()


@pytest.mark.asyncio
async def test_research_tool_propagates_tavily_failure(
    monkeypatch,
):
    monkeypatch.setenv(
        "TAVILY_API_KEY",
        "test-key",
    )

    fake_client = FakeTavilyClient(
        error=RuntimeError("Tavily unavailable")
    )

    monkeypatch.setattr(
        "src.tools.research_tool.AsyncTavilyClient",
        lambda api_key: fake_client,
    )

    tool = ResearchTool()

    with pytest.raises(
        RuntimeError,
        match="Tavily unavailable",
    ):
        await tool.search("AI agents")