"""add logo_x to public_links

Revision ID: d4a2e6b9c1f8
Revises: c3f7a1b8e2d5
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4a2e6b9c1f8'
down_revision: Union[str, Sequence[str], None] = 'c3f7a1b8e2d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('public_links', sa.Column('logo_x', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    op.drop_column('public_links', 'logo_x')
