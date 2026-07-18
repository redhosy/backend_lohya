"""populate_kemungkinan_penyebab

Revision ID: 1b6333515e1e
Revises: a6287417006a
Create Date: 2026-06-22 20:21:26.160783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision: str = '1b6333515e1e'
down_revision: Union[str, Sequence[str], None] = 'a6287417006a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Populate kemungkinan_penyebab for old records."""
    conn = op.get_bind()

    riwayat_rows = conn.execute(
        sa.text("""
            SELECT id_riwayat, id_kategori, kategori_utama 
            FROM riwayat_klasifikasi 
            WHERE kemungkinan_penyebab IS NULL
        """)
    ).fetchall()

    for row in riwayat_rows:
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
                    SELECT DISTINCT r.nama_penyebab 
                    FROM referensi_penyebab r
                    JOIN kategori_klasifikasi k ON r.id_kategori = k.id_kategori
                    WHERE k.kategori = :kategori
                """),
                {"kategori": kategori_utama}
            ).fetchall()
            nama_list = [r[0] for r in ref_rows]

        if nama_list:
            conn.execute(
                sa.text("""
                    UPDATE riwayat_klasifikasi 
                    SET kemungkinan_penyebab = :data 
                    WHERE id_riwayat = :id
                """),
                {"data": json.dumps(nama_list), "id": id_riwayat}
            )


def downgrade() -> None:
    """Revert kemungkinan_penyebab to NULL for migrated records."""
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            UPDATE riwayat_klasifikasi 
            SET kemungkinan_penyebab = NULL 
            WHERE kemungkinan_penyebab IS NOT NULL
        """)
    )
