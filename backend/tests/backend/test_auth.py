"""
Authentication tests: registration, login, token refresh, /auth/me, and
rejection of bad credentials.
"""
import pytest


@pytest.mark.asyncio
async def test_register_creates_active_student(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "student"
    assert body["status"] == "active"
    assert body["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": registered_user["email"],
            "username": "differentusername",
            "password": "Password123",
            "full_name": "Someone Else",
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "username": "weakpass",
            "password": "alllowercase",  # no digit, no uppercase
            "full_name": "Weak Password",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success_returns_tokens(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": registered_user["email"], "password": "WrongPassword123"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client, auth_headers, registered_user):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == registered_user["email"]


@pytest.mark.asyncio
async def test_refresh_rotates_token(client, registered_user):
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert new_tokens["refresh_token"] != refresh_token

    # The old refresh token should now be revoked (single-use rotation).
    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_resp.status_code == 401
