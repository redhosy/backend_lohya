"""ubah status laporan ke enum

Revision ID: laporan_status_enum
Revises: 2cc9c2ec9d58
Create Date: 2026-07-18

"""
from alembic import op
import sqlalchemy as sa


revision = 'laporan_status_enum'
down_revision = '2cc9c2ec9d58'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE laporan_baru ALTER COLUMN status TYPE VARCHAR(20)")
    op.execute("UPDATE laporan_baru SET status = 'pending' WHERE status IS NULL OR status = ''")
    op.alter_column('laporan_baru', 'status',
                    existing_type=sa.String(50),
                    nullable=False,
                    server_default='pending')


def downgrade() -> None:
    op.alter_column('laporan_baru', 'status',
                    existing_type=sa.String(20),
                    nullable=True,
                    server_default=None)
