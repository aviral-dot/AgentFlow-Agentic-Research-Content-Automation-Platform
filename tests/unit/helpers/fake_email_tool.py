class FakeEmailTool:
    """Fake email tool used by integration tests."""

    def __init__(self):
        self.send_count = 0
        self.last_call = None

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
    ):
        self.send_count += 1

        self.last_call = {
            "to": to,
            "subject": subject,
            "body": body,
        }

        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "body": body,
        }