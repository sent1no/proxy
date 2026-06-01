"""placeholder for encrypted fields migration

Revision ID: a1b2c3d4e5f6
Revises: 7457b17f9c8d
Create Date: 2026-06-01 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision = '7457b17f9c8d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: encrypted fields are part of the base schema now.
    return None


def downgrade() -> None:
    # No-op downgrade to preserve Alembic linear history.
    return None
