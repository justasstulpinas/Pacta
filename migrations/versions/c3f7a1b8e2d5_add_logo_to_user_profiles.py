"""add logo to user_profiles

Revision ID: c3f7a1b8e2d5
Revises: b1e4c9d2f037
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3f7a1b8e2d5'
down_revision: Union[str, Sequence[str], None] = 'b1e4c9d2f037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_profiles', sa.Column('logo_image', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('logo_x', sa.Float(), nullable=False, server_default='5.0'))
    op.add_column('user_profiles', sa.Column('logo_y', sa.Float(), nullable=False, server_default='5.0'))


def downgrade() -> None:
    op.drop_column('user_profiles', 'logo_y')
    op.drop_column('user_profiles', 'logo_x')
    op.drop_column('user_profiles', 'logo_image')
