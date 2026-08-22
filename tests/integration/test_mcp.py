import base64
from email import message_from_bytes
from unittest.mock import MagicMock, patch

from gmail_mcp_server import send_email


def test_send_email_success():
    mock_gmail = MagicMock()

    mock_gmail.users.return_value.messages.return_value.send.return_value.execute.return_value = {
        "id": "message-123"
    }

    with patch(
        "gmail_mcp_server.get_gmail_service",
        return_value=mock_gmail,
    ):
        result = send_email(
            to="test@example.com",
            subject="Test",
            body="Hello",
        )

    assert result == {
        "success": True,
        "message": "Email sent successfully",
        "message_id": "message-123",
    }

    send_mock = (
        mock_gmail
        .users.return_value
        .messages.return_value
        .send
    )

    send_mock.assert_called_once()

    kwargs = send_mock.call_args.kwargs

    assert kwargs["userId"] == "me"

    gmail_message = kwargs["body"]

    raw_message = gmail_message["raw"]

    decoded = base64.urlsafe_b64decode(
        raw_message
    )

    email = message_from_bytes(decoded)

    assert email["To"] == "test@example.com"
    assert email["Subject"] == "Test"

    assert email.get_payload() == "Hello"