"""baseline

Revision ID: 0001_baseline
Revises:
Create Date: 2026-11-10

Establishes the Alembic migration chain. No domain tables are created
here; schema migrations are introduced per phase as modules are built.
"""

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
