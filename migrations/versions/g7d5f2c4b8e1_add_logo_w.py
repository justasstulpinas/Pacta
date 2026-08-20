"""add logo_w to templates and links

Revision ID: g7d5f2c4b8e1
Revises: f6c4e8d1b0a3
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'g7d5f2c4b8e1'
down_revision: Union[str, Sequence[str], None] = 'f6c4e8d1b0a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('contract_templates', sa.Column('logo_w', sa.Float(), nullable=False, server_default='15.0'))
    op.add_column('public_links', sa.Column('logo_w', sa.Float(), nullable=False, server_default='15.0'))

def downgrade() -> None:
    op.drop_column('public_links', 'logo_w')
    op.drop_column('contract_templates', 'logo_w')
