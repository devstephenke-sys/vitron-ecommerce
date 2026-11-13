"""Phase 2 identity tests: register, login, refresh rotation, logout,
password reset, /me and address ownership — all against a real database."""

import pytest
from app.modules.identity import service
from fastapi.testclient import TestClient

from .conftest import (
    auth_headers,
    register_payload,
)

BASE = "/api/v1"


def _register(client: TestClient, email: str, password: str = "correct horse battery"):
    return client.post(f"{BASE}/auth/register", json=register_payload(email, password))


def _login(client: TestClient, email: str, password: str = "correct horse battery"):
    return client.post(f"{BASE}/auth/login", json={"email": email, "password": password})


class TestRegister:
    def test_register_returns_tokens_and_customer_permissions(self, db_client: TestClient) -> None:
        response = _register(db_client, "Alice@Example.com")
        assert response.status_code == 201
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == "alice@example.com"  # normalized
        assert body["permissions"] == []  # customer role has no admin permissions

    def test_register_duplicate_email_conflicts(self, db_client: TestClient) -> None:
        assert _register(db_client, "dup@example.com").status_code == 201
        assert _register(db_client, "DUP@example.com").status_code == 409

    def test_register_weak_password_rejected(self, db_client: TestClient) -> None:
        response = _register(db_client, "weak@example.com", password="short")
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, db_client: TestClient) -> None:
        _register(db_client, "bob@example.com")
        response = _login(db_client, "bob@example.com")
        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_login_wrong_password(self, db_client: TestClient) -> None:
        _register(db_client, "carol@example.com")
        response = _login(db_client, "carol@example.com", password="wrong password")
        assert response.status_code == 401

    def test_login_unknown_email_same_error(self, db_client: TestClient) -> None:
        response = _login(db_client, "nobody@example.com")
        assert response.status_code == 401


class TestMe:
    def test_me_requires_auth(self, db_client: TestClient) -> None:
        assert db_client.get(f"{BASE}/me").status_code == 401

    def test_me_rejects_garbage_token(self, db_client: TestClient) -> None:
        response = db_client.get(f"{BASE}/me", headers=auth_headers("not-a-jwt"))
        assert response.status_code == 401

    def test_me_returns_profile_and_permissions(self, db_client: TestClient) -> None:
        token = _register(db_client, "dave@example.com").json()["access_token"]
        response = db_client.get(f"{BASE}/me", headers=auth_headers(token))
        assert response.status_code == 200
        body = response.json()
        assert body["user"]["email"] == "dave@example.com"
        assert body["permissions"] == []

    def test_patch_me_updates_profile(self, db_client: TestClient) -> None:
        token = _register(db_client, "erin@example.com").json()["access_token"]
        response = db_client.patch(
            f"{BASE}/me",
            json={"display_name": "Erin New", "phone": "+254700000001"},
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["user"]["display_name"] == "Erin New"


class TestRefreshRotation:
    def test_refresh_rotates_token(self, db_client: TestClient) -> None:
        tokens = _login_after_register(db_client, "fred@example.com")
        response = db_client.post(
            f"{BASE}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 200
        new_body = response.json()
        assert new_body["refresh_token"] != tokens["refresh_token"]
        assert new_body["access_token"]

    def test_refresh_reuse_revokes_family(self, db_client: TestClient) -> None:
        tokens = _login_after_register(db_client, "gina@example.com")
        first = tokens["refresh_token"]
        rotated = db_client.post(f"{BASE}/auth/refresh", json={"refresh_token": first})
        assert rotated.status_code == 200
        newest = rotated.json()["refresh_token"]

        # Replaying the OLD token must be detected as reuse.
        replay = db_client.post(f"{BASE}/auth/refresh", json={"refresh_token": first})
        assert replay.status_code == 401

        # The whole family is now revoked — even the legitimately rotated token fails.
        after = db_client.post(f"{BASE}/auth/refresh", json={"refresh_token": newest})
        assert after.status_code == 401

    def test_refresh_with_unknown_token(self, db_client: TestClient) -> None:
        response = db_client.post(f"{BASE}/auth/refresh", json={"refresh_token": "bogus-token"})
        assert response.status_code == 401


def _login_after_register(client: TestClient, email: str) -> dict:
    assert _register(client, email).status_code == 201
    return _login(client, email).json()


class TestLogout:
    def test_logout_revokes_refresh_token(self, db_client: TestClient) -> None:
        tokens = _login_after_register(db_client, "henry@example.com")
        response = db_client.post(
            f"{BASE}/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers=auth_headers(tokens["access_token"]),
        )
        assert response.status_code == 204
        refresh = db_client.post(
            f"{BASE}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh.status_code == 401

    def test_logout_requires_auth(self, db_client: TestClient) -> None:
        response = db_client.post(f"{BASE}/auth/logout", json={})
        assert response.status_code == 401


class TestPasswordReset:
    def test_reset_request_never_reveals_existence(self, db_client: TestClient) -> None:
        _register(db_client, "ivan@example.com")
        existing = db_client.post(
            f"{BASE}/auth/password-reset/request", json={"email": "ivan@example.com"}
        )
        missing = db_client.post(
            f"{BASE}/auth/password-reset/request", json={"email": "ghost@example.com"}
        )
        assert existing.status_code == missing.status_code == 202
        assert existing.json() == missing.json()

    def test_reset_confirm_with_invalid_token(self, db_client: TestClient) -> None:
        _register(db_client, "judy@example.com")
        response = db_client.post(
            f"{BASE}/auth/password-reset/confirm",
            json={"token": "bogus", "new_password": "brand new password"},
        )
        assert response.status_code == 400

    def test_reset_confirm_changes_password_and_kills_sessions(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        tokens = _login_after_register(db_client, "kate@example.com")

        # Deterministic token so the test can complete the flow; the raw
        # token is never stored (only its SHA-256 hash).
        monkeypatch.setattr(service.secrets, "token_urlsafe", lambda n: "fixed-reset-token")
        request = db_client.post(
            f"{BASE}/auth/password-reset/request", json={"email": "kate@example.com"}
        )
        monkeypatch.undo()
        assert request.status_code == 202

        confirm = db_client.post(
            f"{BASE}/auth/password-reset/confirm",
            json={"token": "fixed-reset-token", "new_password": "a totally new password"},
        )
        assert confirm.status_code == 204

        # Old password no longer works; new one does.
        assert _login(db_client, "kate@example.com").status_code == 401
        assert (
            _login(db_client, "kate@example.com", password="a totally new password").status_code
            == 200
        )
        # Previous refresh token was revoked by the reset.
        refresh = db_client.post(
            f"{BASE}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh.status_code == 401


class TestRateLimit:
    def test_login_rate_limited(self, db_client: TestClient) -> None:
        for _ in range(10):
            db_client.post(f"{BASE}/auth/login", json={"email": "x@x.com", "password": "y" * 8})
        response = db_client.post(
            f"{BASE}/auth/login", json={"email": "x@x.com", "password": "y" * 8}
        )
        assert response.status_code == 429


ADDRESS = {
    "recipient_name": "Test User",
    "phone": "+254700000002",
    "line1": "1 Test Street",
    "city": "Nairobi",
    "country_code": "ke",
}


class TestAddresses:
    def _token(self, client: TestClient, email: str) -> str:
        return _register(client, email).json()["access_token"]

    def test_address_crud_and_ownership(self, db_client: TestClient) -> None:
        token_a = self._token(db_client, "addr-a@example.com")
        token_b = self._token(db_client, "addr-b@example.com")

        created = db_client.post(
            f"{BASE}/me/addresses", json=ADDRESS, headers=auth_headers(token_a)
        )
        assert created.status_code == 201
        address_id = created.json()["id"]
        assert created.json()["country_code"] == "KE"  # normalized to upper

        # Owner can list and update.
        listed = db_client.get(f"{BASE}/me/addresses", headers=auth_headers(token_a))
        assert len(listed.json()) == 1
        updated = db_client.patch(
            f"{BASE}/me/addresses/{address_id}",
            json={"city": "Mombasa"},
            headers=auth_headers(token_a),
        )
        assert updated.status_code == 200
        assert updated.json()["city"] == "Mombasa"

        # Other user cannot see or modify it (object-level authorization).
        assert (
            db_client.patch(
                f"{BASE}/me/addresses/{address_id}",
                json={"city": "Evil"},
                headers=auth_headers(token_b),
            ).status_code
            == 404
        )
        assert db_client.get(f"{BASE}/me/addresses", headers=auth_headers(token_b)).json() == []

        assert (
            db_client.delete(
                f"{BASE}/me/addresses/{address_id}", headers=auth_headers(token_a)
            ).status_code
            == 204
        )

    def test_default_address_exclusive(self, db_client: TestClient) -> None:
        token = self._token(db_client, "addr-c@example.com")
        first = db_client.post(
            f"{BASE}/me/addresses",
            json={**ADDRESS, "is_default": True},
            headers=auth_headers(token),
        ).json()
        second = db_client.post(
            f"{BASE}/me/addresses",
            json={**ADDRESS, "line1": "2 Other Street", "is_default": True},
            headers=auth_headers(token),
        ).json()
        listed = db_client.get(f"{BASE}/me/addresses", headers=auth_headers(token)).json()
        defaults = [a for a in listed if a["is_default"]]
        assert len(defaults) == 1
        assert defaults[0]["id"] == second["id"]
        assert first["id"] != second["id"]
