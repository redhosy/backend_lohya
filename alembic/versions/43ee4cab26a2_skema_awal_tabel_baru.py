"""skema_awal_tabel_baru

Revision ID: 43ee4cab26a2
Revises: 
Create Date: 2026-06-22 02:36:06.173725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json
from pathlib import Path

# revision identifiers, used by Alembic.
revision: str = '43ee4cab26a2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DATA_DIR = Path(__file__).resolve().parents[2] / "app" / "data"


def seed_kategori_dan_referensi():
    """Seed data kategori_klasifikasi dan referensi_penyebab dari disease_metadata.json."""
    metadata_path = DATA_DIR / "disease_metadata.json"
    if not metadata_path.exists():
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = op.get_bind()

    for item in data:
        conn.execute(
            sa.text("""
                INSERT INTO kategori_klasifikasi (kode_kelas, nama_tampilan, deskripsi, perawatan, pencegahan, is_default)
                VALUES (:kode, :nama, :deskripsi, :perawatan, :pencegahan, :is_default)
                ON CONFLICT (kode_kelas) DO NOTHING
            """),
            {
                "kode": item["slug"],
                "nama": item["kategori"],
                "deskripsi": item.get("deskripsi"),
                "perawatan": json.dumps(item.get("perawatan", [])),
                "pencegahan": json.dumps(item.get("pencegahan", [])),
                "is_default": item["slug"] == "daun_sehat",
            }
        )

        result = conn.execute(
            sa.text("SELECT id_kategori FROM kategori_klasifikasi WHERE kode_kelas = :kode"),
            {"kode": item["slug"]}
        )
        id_kategori = result.scalar()

        for ref in item.get("referensi_penyebab", []):
            conn.execute(
                sa.text("""
                    INSERT INTO referensi_penyebab (id_kategori, nama_penyebab, jenis_penyebab)
                    VALUES (:id_kategori, :nama, :jenis)
                """),
                {
                    "id_kategori": id_kategori,
                    "nama": ref["nama"],
                    "jenis": ref["jenis"],
                }
            )


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('riwayat_diagnosa')
    op.drop_table('edukasi_petani')
    op.drop_table('penyakit')

    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_history_id'))

    op.drop_table('history')

    seed_kategori_dan_referensi()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM referensi_penyebab")
    op.execute("DELETE FROM kategori_klasifikasi")

    op.create_table('history',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('prediction_label', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('confidence_score', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('image_path', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('history_pkey'))
    )
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_history_id'), ['id'], unique=False)

    op.create_table('penyakit',
    sa.Column('id_penyakit', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('kategori', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('nama_penyakit', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('deskripsi', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('perawatan', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('pencegahan', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('is_default', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id_penyakit', name=op.f('penyakit_pkey'))
    )
    op.create_table('edukasi_petani',
    sa.Column('id_edukasi', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('judul', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
    sa.Column('kategori', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('jenis_penyakit', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('gambar', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id_edukasi', name=op.f('edukasi_petani_pkey'))
    )
    op.create_table('riwayat_diagnosa',
    sa.Column('id_riwayat', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id_user', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_penyakit', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('hasil_prediksi', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('akurasi', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
    sa.Column('gambar', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIME(), autoincrement=False, nullable=True),
    sa.Column('distribusi', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_penyakit'], ['penyakit.id_penyakit'], name=op.f('riwayat_diagnosa_id_penyakit_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['id_user'], ['users.id_user'], name=op.f('riwayat_diagnosa_id_user_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_riwayat', name=op.f('riwayat_diagnosa_pkey'))
    )
