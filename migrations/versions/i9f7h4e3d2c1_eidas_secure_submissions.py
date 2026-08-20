"""eIDAS secure submissions: add submissions and signing_audit_trails tables,
drop submitted_data and rendered_content from filled_contracts

Revision ID: i9f7h4e3d2c1
Revises: h8e6g3d2a5b0
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'i9f7h4e3d2c1'
down_revision: Union[str, Sequence[str], None] = 'h8e6g3d2a5b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. New: submissions table
    # ------------------------------------------------------------------
    op.create_table(
        'submissions',
        sa.Column('uuid', sa.String(36), primary_key=True),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('contract_templates.id'), nullable=False),
        sa.Column('template_version_id', sa.Integer(), sa.ForeignKey('contract_template_versions.id'), nullable=True),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('recipient_email', sa.String(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_content', sa.String(), nullable=True),
        # Access code (Argon2 hash only)
        sa.Column('access_code_hash', sa.String(), nullable=False),
        sa.Column('access_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('access_locked_until', sa.DateTime(), nullable=True),
        # Owner download code (Argon2 hash only)
        sa.Column('owner_download_code_hash', sa.String(), nullable=True),
        sa.Column('owner_download_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('owner_download_locked_until', sa.DateTime(), nullable=True),
        # Encrypted PDF (key is never stored)
        sa.Column('encrypted_pdf_blob', sa.LargeBinary(), nullable=True),
        sa.Column('encryption_nonce', sa.LargeBinary(), nullable=True),
        # Signature image (base64 data URI, for audit only)
        sa.Column('signature_image', sa.String(), nullable=True),
        # Layout positions
        sa.Column('logo_x', sa.String(), nullable=True),
        sa.Column('logo_y', sa.String(), nullable=True),
        sa.Column('logo_w', sa.String(), nullable=True),
        sa.Column('client_sig_x', sa.String(), nullable=True),
        sa.Column('client_sig_y', sa.String(), nullable=True),
        sa.Column('user_sig_x', sa.String(), nullable=True),
        sa.Column('user_sig_y', sa.String(), nullable=True),
        # Status and timestamps
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=True),
        sa.Column('downloaded_at', sa.DateTime(), nullable=True),
    )

    # ------------------------------------------------------------------
    # 2. New: signing_audit_trails table (immutable, never deleted)
    # ------------------------------------------------------------------
    op.create_table(
        'signing_audit_trails',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('submission_uuid', sa.String(36), sa.ForeignKey('submissions.uuid'), nullable=False, unique=True),
        sa.Column('document_hash', sa.String(64), nullable=False),
        sa.Column('recipient_email', sa.String(), nullable=True),
        sa.Column('recipient_ip', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('browser_language', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('screen_resolution', sa.String(), nullable=True),
        sa.Column('signer_full_name', sa.String(), nullable=False),
        sa.Column('confirmed_read', sa.Boolean(), nullable=False),
        sa.Column('confirmed_esign', sa.Boolean(), nullable=False),
        sa.Column('code_verified_at', sa.DateTime(), nullable=False),
        sa.Column('contract_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('creator_ip', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # 3. Drop sensitive columns from filled_contracts (legacy table)
    # ------------------------------------------------------------------
    op.drop_column('filled_contracts', 'submitted_data')
    op.drop_column('filled_contracts', 'rendered_content')


def downgrade() -> None:
    # Restore dropped columns on filled_contracts
    op.add_column('filled_contracts', sa.Column('rendered_content', sa.Text(), nullable=True))
    op.add_column('filled_contracts', sa.Column('submitted_data', sa.JSON(), nullable=True))

    op.drop_table('signing_audit_trails')
    op.drop_table('submissions')
