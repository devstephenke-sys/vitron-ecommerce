"""Tests for Phase 1 foundation endpoints and error handling."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_liveness(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-request-id" in response.headers


def test_readiness_ok(ready_client: TestClient) -> None:
    response = ready_client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_readiness_not_ready(not_ready_client: TestClient) -> None:
    response = not_ready_client.get("/api/v1/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["database"] == "unavailable"
    # No internal exception details leak to the client.
    assert "simulated database failure" not in response.text


def test_request_id_propagated(client: TestClient) -> None:
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "test-id-123"})
    assert response.headers["x-request-id"] == "test-id-123"


def test_not_found_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "http_error"
    assert body["error"]["request_id"]


def test_unhandled_error_envelope(app: FastAPI, client: TestClient) -> None:
    @app.get("/api/v1/_test-boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    response = client.get("/api/v1/_test-boom")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "request_id" in body["error"]
