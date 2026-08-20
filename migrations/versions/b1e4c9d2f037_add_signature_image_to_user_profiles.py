"""add signature_image to user_profiles

Revision ID: b1e4c9d2f037
Revises: fba05d61f1aa
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1e4c9d2f037'
down_revision: Union[str, Sequence[str], None] = 'fba05d61f1aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_profiles', sa.Column('signature_image', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('user_profiles', 'signature_image')
