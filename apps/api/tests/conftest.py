"""Shared test fixtures."""

from collections.abc import AsyncIterator

import pytest
from app.db.session import get_db_session
from app.main import create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


class StubSession:
    """Minimal async-session stand-in for dependency overrides."""

    def __init__(self, fail: bool = False) -> None:
        self._fail = fail

    async def execute(self, statement):  # noqa: ANN001, ANN202
        if self._fail:
            raise ConnectionError("simulated database failure")
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


def _override_db(fail: bool):
    async def _session() -> AsyncIterator[AsyncSession]:
        yield StubSession(fail=fail)  # type: ignore[misc]

    return _session


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def ready_client(app: FastAPI) -> TestClient:
    app.dependency_overrides[get_db_session] = _override_db(fail=False)
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def not_ready_client(app: FastAPI) -> TestClient:
    app.dependency_overrides[get_db_session] = _override_db(fail=True)
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
