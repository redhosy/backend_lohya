"""hapus_nama_tampilan_tambah_kategori

Revision ID: a6287417006a
Revises: 26883424cf34
Create Date: 2026-06-22 14:14:41.189545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6287417006a'
down_revision: Union[str, Sequence[str], None] = '26883424cf34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

KATEGORI_MAP = {
    "daun_bercak": "Bercak",
    "daun_keriting": "Keriting",
    "daun_sehat": "Sehat",
}


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('kategori_klasifikasi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('kategori', sa.String(length=50), nullable=True))

    conn = op.get_bind()
    for kode, nama in KATEGORI_MAP.items():
        conn.execute(
            sa.text("UPDATE kategori_klasifikasi SET kategori = :nama WHERE kode_kelas = :kode"),
            {"nama": nama, "kode": kode}
        )

    conn.execute(
        sa.text("""
            UPDATE riwayat_klasifikasi 
            SET kategori_utama = CASE 
                WHEN kategori_utama = 'Daun Bercak' THEN 'Bercak'
                WHEN kategori_utama = 'Daun Keriting' THEN 'Keriting'
                WHEN kategori_utama = 'Daun Sehat' THEN 'Sehat'
                ELSE kategori_utama
            END
        """)
    )

    with op.batch_alter_table('kategori_klasifikasi', schema=None) as batch_op:
        batch_op.alter_column('kategori', nullable=False)
        batch_op.drop_column('nama_tampilan')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('kategori_klasifikasi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nama_tampilan', sa.VARCHAR(length=100), nullable=True))

    conn = op.get_bind()
    for kode, nama in KATEGORI_MAP.items():
        conn.execute(
            sa.text("UPDATE kategori_klasifikasi SET nama_tampilan = :nama WHERE kode_kelas = :kode"),
            {"nama": nama, "kode": kode}
        )

    conn.execute(
        sa.text("""
            UPDATE riwayat_klasifikasi 
            SET kategori_utama = CASE 
                WHEN kategori_utama = 'Bercak' THEN 'Daun Bercak'
                WHEN kategori_utama = 'Keriting' THEN 'Daun Keriting'
                WHEN kategori_utama = 'Sehat' THEN 'Daun Sehat'
                ELSE kategori_utama
            END
        """)
    )

    with op.batch_alter_table('kategori_klasifikasi', schema=None) as batch_op:
        batch_op.alter_column('nama_tampilan', nullable=False)
        batch_op.drop_column('kategori')
