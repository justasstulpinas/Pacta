"""fix content nullable sqlite batch

Revision ID: f42b625c2209
Revises: fa3ab10b66eb
Create Date: 2026-08-25 18:15:04.852084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f42b625c2209'
down_revision: Union[str, Sequence[str], None] = 'fa3ab10b66eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("contract_templates") as batch_op:
        batch_op.alter_column("content", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("contract_templates") as batch_op:
        batch_op.alter_column("content", existing_type=sa.Text(), nullable=False)
