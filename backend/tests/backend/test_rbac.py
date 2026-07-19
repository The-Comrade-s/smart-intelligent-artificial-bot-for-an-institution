"""
RBAC tests: confirm role-gated endpoints reject students and accept admins,
and that a fresh student truly can't self-elevate.
"""
import pytest
from sqlalchemy import select

from app.models.enums import AccountStatus, UserRole
from app.models.user import User


@pytest.mark.asyncio
async def test_student_cannot_list_users(client, auth_headers):
    resp = await client.get("/api/v1/users", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_create_course(client, auth_headers):
    resp = await client.post(
        "/api/v1/courses",
        headers=auth_headers,
        json={"code": "CSC101", "title": "Intro to CS", "level": "ND I", "semester": "First", "department_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(client, db_session, auth_headers):
    # Promote the test student directly in the DB rather than via the API,
    # since role changes are themselves super-admin gated.
    result = await db_session.execute(select(User).where(User.email == "student@example.com"))
    user = result.scalar_one()
    user.role = UserRole.ADMIN
    await db_session.commit()

    resp = await client.get("/api/v1/users", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_cannot_change_roles_only_super_admin_can(client, db_session, auth_headers):
    result = await db_session.execute(select(User).where(User.email == "student@example.com"))
    user = result.scalar_one()
    user.role = UserRole.ADMIN
    other_user_id = user.id
    await db_session.commit()

    resp = await client.patch(
        f"/api/v1/users/{other_user_id}/role", headers=auth_headers, params={"new_role": "administrator"}
    )
    # A plain admin (not super admin) must be rejected here.
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_suspended_account_is_rejected(client, db_session, auth_headers):
    result = await db_session.execute(select(User).where(User.email == "student@example.com"))
    user = result.scalar_one()
    user.status = AccountStatus.SUSPENDED
    await db_session.commit()

    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 403
