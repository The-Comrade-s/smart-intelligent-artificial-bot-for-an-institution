"""
Chat and conversation tests. These exercise the mock AI provider (no API
key needed) end to end: send a message, get a persisted conversation with
a real assistant reply, then exercise conversation history endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_send_message_creates_conversation(client, auth_headers):
    resp = await client.post(
        "/api/v1/chat", headers=auth_headers, json={"conversation_id": None, "message": "What is a linked list?"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["conversation_id"]
    assert body["message"]["role"] == "assistant"
    assert body["message"]["content"]  # mock provider always returns something
    assert isinstance(body["suggestions"], list)


@pytest.mark.asyncio
async def test_conversation_appears_in_history(client, auth_headers):
    send_resp = await client.post(
        "/api/v1/chat", headers=auth_headers, json={"conversation_id": None, "message": "Explain recursion"}
    )
    conversation_id = send_resp.json()["conversation_id"]

    list_resp = await client.get("/api/v1/conversations", headers=auth_headers)
    assert list_resp.status_code == 200
    ids = [c["id"] for c in list_resp.json()]
    assert conversation_id in ids

    detail_resp = await client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    messages = detail_resp.json()["messages"]
    assert len(messages) == 2  # user message + assistant reply
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_cannot_access_another_users_conversation(client, auth_headers):
    # Create a conversation as the primary test user.
    send_resp = await client.post(
        "/api/v1/chat", headers=auth_headers, json={"conversation_id": None, "message": "Hello"}
    )
    conversation_id = send_resp.json()["conversation_id"]

    # A second, different user should not be able to read it.
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "otheruser@example.com",
            "username": "otheruser",
            "password": "Password123",
            "full_name": "Other User",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "otheruser@example.com", "password": "Password123"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resp = await client.get(f"/api/v1/conversations/{conversation_id}", headers=other_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_rename_and_pin_conversation(client, auth_headers):
    send_resp = await client.post(
        "/api/v1/chat", headers=auth_headers, json={"conversation_id": None, "message": "Hi"}
    )
    conversation_id = send_resp.json()["conversation_id"]

    rename_resp = await client.patch(
        f"/api/v1/conversations/{conversation_id}/rename", headers=auth_headers, json={"title": "My renamed chat"}
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["title"] == "My renamed chat"

    pin_resp = await client.patch(f"/api/v1/conversations/{conversation_id}/pin", headers=auth_headers)
    assert pin_resp.status_code == 200
    assert pin_resp.json()["is_pinned"] is True
