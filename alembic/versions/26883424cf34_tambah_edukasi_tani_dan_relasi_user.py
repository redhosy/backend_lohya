"""tambah_edukasi_tani_dan_relasi_user

Revision ID: 26883424cf34
Revises: 43ee4cab26a2
Create Date: 2026-06-22 04:14:23.841997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json
from pathlib import Path

# revision identifiers, used by Alembic.
revision: str = '26883424cf34'
down_revision: Union[str, Sequence[str], None] = '43ee4cab26a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DATA_DIR = Path(__file__).resolve().parents[2] / "app" / "data"


def seed_edukasi_tani():
    """Seed data edukasi_tani dari farmer_education.json."""
    edukasi_path = DATA_DIR / "farmer_education.json"
    if not edukasi_path.exists():
        return

    with open(edukasi_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = op.get_bind()

    for item in data:
        isi_text = ""
        if item.get("isi"):
            parts = []
            for section in item["isi"]:
                parts.append(f"## {section['subjudul']}\n{section['konten']}")
            isi_text = "\n\n".join(parts)

        gambar_url = None
        if item.get("image") and item["image"].get("url"):
            gambar_url = item["image"]["url"]

        conn.execute(
            sa.text("""
                INSERT INTO edukasi_tani (judul, kategori, gambar, jenis_diagnosa, content)
                VALUES (:judul, :kategori, :gambar, :jenis_diagnosa, :content)
            """),
            {
                "judul": item.get("judul", ""),
                "kategori": item.get("kategori", ""),
                "gambar": gambar_url,
                "jenis_diagnosa": item.get("kategori", "").replace("daun_", "").replace("_", " ").title(),
                "content": isi_text,
            }
        )


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('edukasi_tani',
    sa.Column('id_edukasi', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('judul', sa.String(length=200), nullable=False),
    sa.Column('kategori', sa.String(length=50), nullable=False),
    sa.Column('gambar', sa.String(length=500), nullable=True),
    sa.Column('jenis_diagnosa', sa.String(length=100), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id_edukasi')
    )
    with op.batch_alter_table('edukasi_tani', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_edukasi_tani_id_edukasi'), ['id_edukasi'], unique=False)
        batch_op.create_index(batch_op.f('ix_edukasi_tani_kategori'), ['kategori'], unique=False)

    seed_edukasi_tani()

    op.execute("ALTER TABLE riwayat_klasifikasi ALTER COLUMN id_user TYPE INTEGER USING id_user::integer")

    with op.batch_alter_table('riwayat_klasifikasi', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_riwayat_id_user', 'users', ['id_user'], ['id_user'], ondelete='CASCADE')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('auth_provider',
               existing_type=postgresql.ENUM('manual', 'google', name='auth_provider'),
               type_=sa.String(length=6),
               existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_users_id_user'), ['id_user'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_id_user'))
        batch_op.alter_column('auth_provider',
               existing_type=sa.String(length=6),
               type_=postgresql.ENUM('manual', 'google', name='auth_provider'),
               existing_nullable=True)

    with op.batch_alter_table('riwayat_klasifikasi', schema=None) as batch_op:
        batch_op.drop_constraint('fk_riwayat_id_user', type_='foreignkey')

    op.execute("ALTER TABLE riwayat_klasifikasi ALTER COLUMN id_user TYPE VARCHAR(100) USING id_user::varchar(100)")

    with op.batch_alter_table('edukasi_tani', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_edukasi_tani_kategori'))
        batch_op.drop_index(batch_op.f('ix_edukasi_tani_id_edukasi'))

    op.drop_table('edukasi_tani')
