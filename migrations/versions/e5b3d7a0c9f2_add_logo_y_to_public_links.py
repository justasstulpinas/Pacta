"""add logo_y to public_links

Revision ID: e5b3d7a0c9f2
Revises: d4a2e6b9c1f8
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e5b3d7a0c9f2'
down_revision: Union[str, Sequence[str], None] = 'd4a2e6b9c1f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('public_links', sa.Column('logo_y', sa.Float(), nullable=False, server_default='5.0'))

def downgrade() -> None:
    op.drop_column('public_links', 'logo_y')
