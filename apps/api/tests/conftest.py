"""Shared test fixtures.

Two tiers:

- Stub-session clients (`client`, `ready_client`, `not_ready_client`) for
  foundation tests that must not require a database.
- `db_client` — a TestClient wired to a real PostgreSQL database (the same
  DATABASE_URL the app uses). The schema is migrated once per test session
  via Alembic, and data tables are truncated between tests. Requires a
  reachable Postgres (docker compose locally, service container in CI).

Engines are created inside whichever event loop uses them: TestClient
runs each request on its own portal loop and helpers use ``asyncio.run``,
so a shared session-scoped engine would bind asyncpg connections to a dead
loop. Per-call engines keep every connection on its owning loop.
"""

import asyncio
import shutil
import subprocess
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from app.core.config import get_settings
from app.core.ratelimit import _limiter
from app.db.session import get_db_session
from app.main import create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

API_ROOT = Path(__file__).resolve().parents[1]


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


# ------------------------------------------------------------ real DB tier


def _new_engine_and_factory() -> tuple[object, async_sessionmaker[AsyncSession]]:
    from sqlalchemy.ext.asyncio import AsyncEngine

    engine: AsyncEngine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    return engine, async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def _migrated_db() -> Iterator[None]:
    """Apply all Alembic migrations once against the test database.

    Runs the real CLI in a subprocess: the local ``alembic/`` package
    shadows the installed ``alembic`` distribution when the API directory
    is on ``sys.path``, so the Python API cannot be imported directly.
    """
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to run migrations in tests"
    subprocess.run(
        [uv, "run", "alembic", "upgrade", "head"],
        cwd=API_ROOT,
        check=True,
    )
    yield


@pytest.fixture()
def db_client(app: FastAPI) -> Iterator[TestClient]:
    """TestClient whose DB dependency uses the real (migrated) database."""

    async def _session() -> AsyncIterator[AsyncSession]:
        engine, factory = _new_engine_and_factory()
        try:
            async with factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        finally:
            await engine.dispose()

    app.dependency_overrides[get_db_session] = _session
    _limiter.reset()
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    _limiter.reset()

    async def _cleanup() -> None:
        engine, factory = _new_engine_and_factory()
        try:
            async with factory() as session:
                # users CASCADE clears user_roles, addresses, customer_profiles,
                # refresh_tokens, password_reset_tokens and auth_events/audit_logs
                # rows linked to users; explicit truncates cover the rest.
                await session.execute(text("TRUNCATE users CASCADE"))
                await session.execute(text("TRUNCATE audit_logs, auth_events, background_jobs"))
                await session.commit()
        finally:
            await engine.dispose()

    asyncio.run(_cleanup())


# ------------------------------------------------------------ helpers


def run_async(coro):  # noqa: ANN001, ANN201
    return asyncio.run(coro)


async def create_user_with_role(
    email: str,
    role_code: str = "customer",
    password: str = "correct horse battery",
) -> str:
    """Insert a user with a seeded role directly; returns user id."""
    from app.modules.identity.models import Role, User, UserRole
    from app.modules.identity.security import hash_password

    engine, factory = _new_engine_and_factory()
    try:
        async with factory() as session:
            user = User(
                email=email,
                password_hash=hash_password(password),
                display_name="Test User",
            )
            session.add(user)
            await session.flush()
            role = (await session.execute(select(Role).where(Role.code == role_code))).scalar_one()
            session.add(UserRole(user_id=user.id, role_id=role.id))
            await session.commit()
            return str(user.id)
    finally:
        await engine.dispose()


def make_user(email: str, role_code: str = "customer") -> str:
    return run_async(create_user_with_role(email, role_code))


@asynccontextmanager
async def open_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a session on a fresh engine; safe inside ``asyncio.run``."""
    engine, factory = _new_engine_and_factory()
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


def register_payload(email: str, password: str = "correct horse battery") -> dict:
    return {"email": email, "password": password, "display_name": "Test User"}


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
