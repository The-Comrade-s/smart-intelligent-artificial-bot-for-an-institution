"""
Shared pytest fixtures for backend tests.

Requires a real PostgreSQL database to run against (models use
PostgreSQL-specific types — UUID, JSONB, ARRAY — so SQLite can't stand in).
Set TEST_DATABASE_URL before running, e.g.:

    export TEST_DATABASE_URL=postgresql+asyncpg://cosib:cosib@localhost:5432/cosib_test
    pytest

If TEST_DATABASE_URL isn't set, these fixtures fall back to DATABASE_URL
from your .env — point that at a disposable database, not production.
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.append(str(Path(__file__).resolve().parents[2]))

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from app.db.base_class import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import *  # noqa: E402,F401,F403  (ensures every model is registered on Base.metadata)

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://cosib:cosib@localhost:5432/cosib_test"
)


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(engine, db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    payload = {
        "email": "student@example.com",
        "username": "teststudent",
        "password": "Password123",
        "full_name": "Test Student",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    return payload


@pytest_asyncio.fixture
async def auth_headers(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
