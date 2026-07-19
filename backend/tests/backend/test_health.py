"""
Health check endpoint test — this is what Railway polls to confirm the
service is alive.
"""
import pytest


@pytest.mark.asyncio
async def test_health_check_reports_ok(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
