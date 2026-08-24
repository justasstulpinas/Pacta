"""add docx_path, make content nullable

Revision ID: fa3ab10b66eb
Revises: ad1c2ea4351c
Create Date: 2026-08-24 19:13:41.680776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa3ab10b66eb'
down_revision: Union[str, Sequence[str], None] = 'ad1c2ea4351c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contract_templates', sa.Column('docx_path', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('contract_templates', 'docx_path')
