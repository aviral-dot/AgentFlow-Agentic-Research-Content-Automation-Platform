import pytest

from src.database import postgres


def test_create_checkpointer_requires_database_url(
    monkeypatch,
):
    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="DATABASE_URL",
    ):
        postgres.create_checkpointer()


def test_create_checkpointer(
    monkeypatch,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test",
    )

    class FakeCheckpointer:
        def __init__(self):
            self.setup_called = False

        def setup(self):
            self.setup_called = True

    fake = FakeCheckpointer()

    class FakePostgresSaver:
        @classmethod
        def from_conn_string(
            cls,
            url,
        ):
            assert (
                url
                == "postgresql://test"
            )
            return fake

    monkeypatch.setattr(
        postgres,
        "PostgresSaver",
        FakePostgresSaver,
    )

    result = (
        postgres.create_checkpointer()
    )

    assert result is fake
    assert fake.setup_called