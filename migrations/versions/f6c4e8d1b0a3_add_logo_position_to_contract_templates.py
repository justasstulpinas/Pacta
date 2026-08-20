"""add logo position to contract_templates

Revision ID: f6c4e8d1b0a3
Revises: e5b3d7a0c9f2
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f6c4e8d1b0a3'
down_revision: Union[str, Sequence[str], None] = 'e5b3d7a0c9f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('contract_templates', sa.Column('logo_x', sa.Float(), nullable=False, server_default='5.0'))
    op.add_column('contract_templates', sa.Column('logo_y', sa.Float(), nullable=False, server_default='5.0'))

def downgrade() -> None:
    op.drop_column('contract_templates', 'logo_y')
    op.drop_column('contract_templates', 'logo_x')
