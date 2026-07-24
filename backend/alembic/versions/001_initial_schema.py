"""Initial schema — scans and api_keys tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-07-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create api_keys table first (referenced by scans)
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("rate_limit", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])

    # Create scans table
    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("image_filename", sa.String(255), nullable=False),
        sa.Column("image_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("ai_verdict", sa.String(10), nullable=True),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("ai_details", postgresql.JSONB(), server_default="{}", nullable=True),
        sa.Column("qr_detected", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("qr_payload", sa.Text(), nullable=True),
        sa.Column("quish_verdict", sa.String(15), nullable=True),
        sa.Column("quish_confidence", sa.Float(), nullable=True),
        sa.Column("quish_details", postgresql.JSONB(), server_default="{}", nullable=True),
        sa.Column("status", sa.String(20), server_default="completed", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("api_key_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("api_keys.id"), nullable=True),
    )
    op.create_index("ix_scans_image_hash", "scans", ["image_hash"])
    op.create_index("ix_scans_created_at", "scans", ["created_at"])
    op.create_index("ix_scans_image_filename", "scans", ["image_filename"])


def downgrade() -> None:
    op.drop_table("scans")
    op.drop_table("api_keys")
