"""fix_sehat_empty_referensi

Revision ID: 905ae0bc78f6
Revises: b1e8e8bbcacf
Create Date: 2026-06-22 20:25:30.620798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision: str = '905ae0bc78f6'
down_revision: Union[str, Sequence[str], None] = 'b1e8e8bbcacf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix: set kemungkinan_penyebab to empty list for kategori with no referensi."""
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("""
            SELECT r.id_riwayat, r.id_kategori, r.kategori_utama
            FROM riwayat_klasifikasi r
        """)
    ).fetchall()

    for row in rows:
        id_riwayat, id_kategori, kategori_utama = row

        nama_list = []

        if id_kategori:
            ref_rows = conn.execute(
                sa.text("""
                    SELECT DISTINCT nama_penyebab 
                    FROM referensi_penyebab 
                    WHERE id_kategori = :id_kategori
                """),
                {"id_kategori": id_kategori}
            ).fetchall()
            nama_list = [r[0] for r in ref_rows]

        if not nama_list and kategori_utama:
            ref_rows = conn.execute(
                sa.text("""
                    SELECT DISTINCT rp.nama_penyebab 
                    FROM referensi_penyebab rp
                    JOIN kategori_klasifikasi kk ON rp.id_kategori = kk.id_kategori
                    WHERE kk.kategori = :kategori
                """),
                {"kategori": kategori_utama}
            ).fetchall()
            nama_list = [r[0] for r in ref_rows]

        conn.execute(
            sa.text("""
                UPDATE riwayat_klasifikasi 
                SET kemungkinan_penyebab = :data 
                WHERE id_riwayat = :id
            """),
            {"data": json.dumps(nama_list), "id": id_riwayat}
        )


def downgrade() -> None:
    """Revert not possible."""
    pass
