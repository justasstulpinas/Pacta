"""add signature positions to templates and links

Revision ID: h8e6g3d2a5b0
Revises: g7d5f2c4b8e1
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'h8e6g3d2a5b0'
down_revision: Union[str, Sequence[str], None] = 'g7d5f2c4b8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('contract_templates', sa.Column('client_sig_x', sa.Float(), nullable=True))
    op.add_column('contract_templates', sa.Column('client_sig_y', sa.Float(), nullable=True))
    op.add_column('contract_templates', sa.Column('user_sig_x', sa.Float(), nullable=True))
    op.add_column('contract_templates', sa.Column('user_sig_y', sa.Float(), nullable=True))
    op.add_column('public_links', sa.Column('client_sig_x', sa.Float(), nullable=True))
    op.add_column('public_links', sa.Column('client_sig_y', sa.Float(), nullable=True))
    op.add_column('public_links', sa.Column('user_sig_x', sa.Float(), nullable=True))
    op.add_column('public_links', sa.Column('user_sig_y', sa.Float(), nullable=True))

def downgrade() -> None:
    for col in ['user_sig_y', 'user_sig_x', 'client_sig_y', 'client_sig_x']:
        op.drop_column('public_links', col)
        op.drop_column('contract_templates', col)
