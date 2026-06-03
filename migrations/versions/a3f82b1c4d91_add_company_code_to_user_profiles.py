"""add company_code to user_profiles

Revision ID: a3f82b1c4d91
Revises: 5126fc3e928f
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f82b1c4d91'
down_revision: Union[str, Sequence[str], None] = '5126fc3e928f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_profiles', sa.Column('company_code', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('user_profiles', 'company_code')
