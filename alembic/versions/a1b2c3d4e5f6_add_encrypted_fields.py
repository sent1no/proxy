"""add_encrypted_fields

Revision ID: a1b2c3d4e5f6
Revises: 7457b17f9c8d
Create Date: 2026-06-01 18:00:00.000000

Практична №7: додаємо зашифровані поля encrypted_email та encrypted_phone.
Стара колонка email залишається тимчасово для міграції даних.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7457b17f9c8d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Додаємо зашифровані поля до таблиці users."""
    # Додаємо encrypted_email (nullable спочатку для сумісності)
    op.add_column('users',
        sa.Column('encrypted_email', sa.String(length=500), nullable=True)
    )
    # Додаємо encrypted_phone
    op.add_column('users',
        sa.Column('encrypted_phone', sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    """Видаляємо зашифровані поля."""
    op.drop_column('users', 'encrypted_phone')
    op.drop_column('users', 'encrypted_email')
