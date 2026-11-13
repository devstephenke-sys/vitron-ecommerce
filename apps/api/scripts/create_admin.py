"""Create or promote an admin user.

Usage (from apps/api):
    uv run python scripts/create_admin.py --email admin@example.com \
        --password 'a-strong-password' [--role administrator]

Creates the user with the given role if they do not exist, or replaces
their roles if they already exist. Passwords are never echoed.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import get_session_factory  # noqa: E402
from app.modules.identity.models import Role, User, UserRole  # noqa: E402
from app.modules.identity.security import hash_password  # noqa: E402
from sqlalchemy import delete, select  # noqa: E402


async def create_admin(email: str, password: str, role_code: str) -> int:
    email = email.strip().lower()
    factory = get_session_factory()
    async with factory() as session:
        role = (
            await session.execute(select(Role).where(Role.code == role_code))
        ).scalar_one_or_none()
        if role is None:
            print(f"error: role '{role_code}' not found — run migrations first", file=sys.stderr)
            return 1

        user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if user is None:
            user = User(email=email, password_hash=hash_password(password), display_name=email)
            session.add(user)
            await session.flush()
            print(f"created user {email} (id={user.id})")
        else:
            user.password_hash = hash_password(password)
            print(f"updated password for existing user {email} (id={user.id})")

        await session.execute(delete(UserRole).where(UserRole.user_id == user.id))
        session.add(UserRole(user_id=user.id, role_id=role.id, assigned_by=user.id))
        await session.commit()
        print(f"assigned role '{role_code}' to {email}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", default="administrator")
    args = parser.parse_args()
    if len(args.password) < 8:
        print("error: password must be at least 8 characters", file=sys.stderr)
        return 1
    return asyncio.run(create_admin(args.email, args.password, args.role))


if __name__ == "__main__":
    raise SystemExit(main())
