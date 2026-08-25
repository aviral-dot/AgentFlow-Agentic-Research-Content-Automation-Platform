RESEARCH_GOLDENS = [
    {
        "input": (
            "Research the latest developments "
            "in AI agents."
        ),
        "expected_topic": "AI agents",
        "expected_properties": [
            "contains a concise summary",
            "contains key findings",
            "does not invent unsupported facts",
        ],
    },
    {
        "input": (
            "Research how planner-executor "
            "agent architectures work."
        ),
        "expected_topic": (
            "planner-executor architectures"
        ),
        "expected_properties": [
            "explains planning",
            "explains execution",
            "remains factually grounded",
        ],
    },
    {
        "input": (
            "Research the role of tool calling "
            "in AI agents."
        ),
        "expected_topic": (
            "tool calling in AI agents"
        ),
        "expected_properties": [
            "explains tool usage",
            "contains factual findings",
            "avoids unsupported claims",
        ],
    },
]