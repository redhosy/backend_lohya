"""convert_kemungkinan_penyebab_to_simple

Revision ID: 7666bcc80f3b
Revises: 1b6333515e1e
Create Date: 2026-06-22 20:22:37.529987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision: str = '7666bcc80f3b'
down_revision: Union[str, Sequence[str], None] = '1b6333515e1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_old_format(data):
    """Check if data is in old format (list of dicts with 'referensi' key)."""
    if not data or not isinstance(data, list):
        return False
    if len(data) == 0:
        return False
    return isinstance(data[0], dict) and 'referensi' in data[0]


def extract_nama_penyebab(data):
    """Extract unique nama_penyebab from old format."""
    nama_set = set()
    for item in data:
        if isinstance(item, dict) and 'referensi' in item:
            for ref in item['referensi']:
                nama_set.add(ref)
    return list(nama_set)


def upgrade() -> None:
    """Convert kemungkinan_penyebab from complex to simple format."""
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT id_riwayat, kemungkinan_penyebab FROM riwayat_klasifikasi WHERE kemungkinan_penyebab IS NOT NULL")
    ).fetchall()

    for row in rows:
        id_riwayat, kemungkinan_penyebab = row

        if is_old_format(kemungkinan_penyebab):
            simple_list = extract_nama_penyebab(kemungkinan_penyebab)
            if simple_list:
                conn.execute(
                    sa.text("UPDATE riwayat_klasifikasi SET kemungkinan_penyebab = :data WHERE id_riwayat = :id"),
                    {"data": json.dumps(simple_list), "id": id_riwayat}
                )


def downgrade() -> None:
    """Revert is not possible - old format data is lost after conversion."""
    pass
