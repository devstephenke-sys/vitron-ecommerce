"""Phase 2 RBAC tests: server-side permission enforcement.

The admin frontend route guard is UX only — these tests prove the API
itself rejects unauthorized callers on protected operations.
"""

from fastapi.testclient import TestClient

from .conftest import auth_headers, make_user, open_db_session, register_payload, run_async

BASE = "/api/v1"


def _token_for(db_client: TestClient, email: str, password: str = "correct horse battery") -> str:
    """Log in a user created directly in the DB (bypasses /auth/register,
    which always assigns the customer role)."""
    response = db_client.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _make_and_login(db_client: TestClient, email: str, role: str) -> str:
    make_user(email, role_code=role)
    return _token_for(db_client, email)


class TestAuditLogEndpoint:
    """GET /admin/audit-logs requires the audit.read permission."""

    def test_administrator_allowed(self, db_client: TestClient) -> None:
        token = _make_and_login(db_client, "admin@example.com", "administrator")
        response = db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token))
        assert response.status_code == 200
        body = response.json()
        assert "items" in body and "total" in body

    def test_customer_forbidden(self, db_client: TestClient) -> None:
        db_client.post(f"{BASE}/auth/register", json=register_payload("cust@example.com"))
        token = _token_for(db_client, "cust@example.com")
        response = db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token))
        assert response.status_code == 403

    def test_sales_staff_forbidden(self, db_client: TestClient) -> None:
        # sales_staff has many permissions but deliberately not audit.read.
        token = _make_and_login(db_client, "sales@example.com", "sales_staff")
        response = db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token))
        assert response.status_code == 403

    def test_inventory_manager_forbidden(self, db_client: TestClient) -> None:
        token = _make_and_login(db_client, "inv@example.com", "inventory_manager")
        response = db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token))
        assert response.status_code == 403

    def test_unauthenticated_rejected(self, db_client: TestClient) -> None:
        assert db_client.get(f"{BASE}/admin/audit-logs").status_code == 401

    def test_permission_checked_per_request_not_cached_in_token(
        self, db_client: TestClient
    ) -> None:
        """Revoking a role must take effect on the next request — the JWT
        carries no permission claims, so there is nothing stale to trust."""
        from app.modules.identity.models import Role, User, UserRole
        from sqlalchemy import delete, select

        token = _make_and_login(db_client, "tempadmin@example.com", "administrator")
        assert (
            db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token)).status_code
            == 200
        )

        async def _strip() -> None:
            async with open_db_session() as session:
                user = (
                    await session.execute(select(User).where(User.email == "tempadmin@example.com"))
                ).scalar_one()
                admin_role = (
                    await session.execute(select(Role).where(Role.code == "administrator"))
                ).scalar_one()
                await session.execute(
                    delete(UserRole).where(
                        UserRole.user_id == user.id, UserRole.role_id == admin_role.id
                    )
                )
                await session.commit()

        run_async(_strip())

        # Same access token now fails — permissions are re-read per request.
        response = db_client.get(f"{BASE}/admin/audit-logs", headers=auth_headers(token))
        assert response.status_code == 403
