from deepeval.test_case import MCPServer, MCPToolCall
from mcp.types import CallToolResult, TextContent, Tool


def build_gmail_mcp_server() -> MCPServer:
    """Build the Gmail MCP server definition used by DeepEval."""

    send_email_tool = Tool(
        name="send_email",
        description="Send an email using Gmail.",
        inputSchema={
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address.",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject.",
                },
                "body": {
                    "type": "string",
                    "description": "Email body.",
                },
            },
            "required": [
                "to",
                "subject",
                "body",
            ],
        },
    )

    return MCPServer(
        server_name="Gmail MCP Server",
        transport="stdio",
        available_tools=[
            send_email_tool,
        ],
    )


def build_send_email_tool_call(
    *,
    to: str,
    subject: str,
    body: str,
) -> MCPToolCall:
    """Build a DeepEval MCP tool-call record."""

    result = CallToolResult(
        content=[
            TextContent(
                type="text",
                text="Email sent successfully.",
            )
        ],
        isError=False,
    )

    return MCPToolCall(
        name="send_email",
        args={
            "to": to,
            "subject": subject,
            "body": body,
        },
        result=result,
    )