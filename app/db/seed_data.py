import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.agen_penyebab_model import AgenPenyebab
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi
from app.models.user_model import User
from app.models.edukasi_tani_model import EdukasiTani
from app.models.kategori_edukasi_model import KategoriEdukasi
from app.models.koleksi_user_model import KoleksiUser

DIREKTORI_DATA = Path(__file__).parent.parent / "data"


def muat_json(nama_file: str) -> list:
    jalur = DIREKTORI_DATA / nama_file
    with open(jalur, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# SEED KATEGORI KLASIFIKASI
# ============================================================

def seed_kategori_klasifikasi(db: Session):
    daftar_penyakit = muat_json("disease_metadata.json")

    for penyakit in daftar_penyakit:
        kode_kelas = penyakit["kode_kelas"]
        sudah_ada = db.query(KategoriKlasifikasi).filter(
            KategoriKlasifikasi.kode_kelas == kode_kelas
        ).first()

        if sudah_ada:
            sudah_ada.kategori = penyakit["kategori"]
            sudah_ada.deskripsi = penyakit.get("deskripsi", "")
            sudah_ada.perawatan = penyakit.get("perawatan", [])
            sudah_ada.pencegahan = penyakit.get("pencegahan", [])
            sudah_ada.referensi = penyakit.get("referensi", [])
            sudah_ada.is_default = True
            print(f"  [UPDATE] Kategori: {kode_kelas}")
        else:
            kategori_baru = KategoriKlasifikasi(
                kode_kelas=kode_kelas,
                kategori=penyakit["kategori"],
                deskripsi=penyakit.get("deskripsi", ""),
                perawatan=penyakit.get("perawatan", []),
                pencegahan=penyakit.get("pencegahan", []),
                referensi=penyakit.get("referensi", []),
                is_default=True,
            )
            db.add(kategori_baru)
            print(f"  [INSERT] Kategori: {kode_kelas}")

    db.commit()
    print("Seed kategori_klasifikasi selesai.")


# ============================================================
# SEED AGEN PENYEBAB
# ============================================================

def seed_agen_penyebab(db: Session):
    daftar_penyakit = muat_json("disease_metadata.json")

    for penyakit in daftar_penyakit:
        kode_kelas = penyakit["kode_kelas"]
        kategori = db.query(KategoriKlasifikasi).filter(
            KategoriKlasifikasi.kode_kelas == kode_kelas
        ).first()

        if not kategori:
            print(f"  [SKIP] Kategori {kode_kelas} tidak ditemukan")
            continue

        sudah_ada = db.query(AgenPenyebab).filter(
            AgenPenyebab.id_kategori == kategori.id_kategori
        ).count()

        if sudah_ada > 0:
            print(f"  [SKIP] {kode_kelas} sudah punya {sudah_ada} agen penyebab")
            continue

        daftar_nama = penyakit.get("nama_ilmiah", [])
        for item in daftar_nama:
            agen_baru = AgenPenyebab(
                id_kategori=kategori.id_kategori,
                nama_ilmiah=item["nama"],
                jenis=item["jenis"],
            )
            db.add(agen_baru)

        print(f"  [INSERT] {len(daftar_nama)} agen penyebab untuk {kode_kelas}")

    db.commit()
    print("Seed agen_penyebab selesai.")


# ============================================================
# SEED KATEGORI EDUKASI
# ============================================================

DAFTAR_KATEGORI_EDUKASI = [
    "Penyakit",
    "Budidaya",
    "Pemupukan",
    "Hama",
    "Lingkungan",
]


def seed_kategori_edukasi(db: Session):
    for nama in DAFTAR_KATEGORI_EDUKASI:
        sudah_ada = db.query(KategoriEdukasi).filter(
            KategoriEdukasi.nama_kategori_edu == nama
        ).first()

        if not sudah_ada:
            kategori_baru = KategoriEdukasi(nama_kategori_edu=nama)
            db.add(kategori_baru)
            print(f"  [INSERT] Kategori edukasi: {nama}")

    db.commit()
    print("Seed kategori_edukasi selesai.")


# ============================================================
# SEED EDUKASI TANI (DARI SEED_EDU.PY)
# ============================================================

def bangun_konten(item: dict) -> str:
    bagian = []
    for isi in item.get("isi", []):
        subjudul = isi.get("subjudul", "")
        konten = isi.get("konten", "")
        if subjudul:
            bagian.append(f"## {subjudul}\n\n{konten}")
        else:
            bagian.append(konten)

    tips = item.get("tips_lapangan", [])
    if tips:
        bagian.append("## Tips Lapangan")
        for i, tip in enumerate(tips, 1):
            bagian.append(f"{i}. {tip}")

    catatan = item.get("catatan")
    if catatan:
        bagian.append(f"## Catatan\n\n{catatan}")

    return "\n\n".join(bagian)


def cari_id_kategori_klasifikasi(db: Session, kode_kelas: str) -> int:
    kategori = db.query(KategoriKlasifikasi).filter(
        KategoriKlasifikasi.kode_kelas == kode_kelas
    ).first()
    return kategori.id_kategori if kategori else None


def cari_id_kategori_edukasi(db: Session, nama_kategori: str) -> int:
    kategori = db.query(KategoriEdukasi).filter(
        KategoriEdukasi.nama_kategori_edu == nama_kategori
    ).first()
    return kategori.id_kategori_edu if kategori else None


def seed_edukasi_tani(db: Session):
    daftar_edukasi = muat_json("edukasi_metadata.json")

    for item in daftar_edukasi:
        judul = item.get("judul", "")
        sudah_ada = db.query(EdukasiTani).filter(
            EdukasiTani.judul == judul
        ).first()

        if sudah_ada:
            print(f"  [SKIP] Sudah ada: {judul[:50]}...")
            continue

        id_klasifikasi = cari_id_kategori_klasifikasi(db, item.get("kategori", ""))
        id_edukasi = cari_id_kategori_edukasi(db, item.get("kategori_edukasi", ""))

        if not id_edukasi:
            print(f"  [SKIP] Kategori edukasi '{item.get('kategori_edukasi')}' tidak ditemukan")
            continue

        gambar = None
        image_data = item.get("image", {})
        if image_data and image_data.get("url"):
            gambar = image_data["url"]

        edukasi_baru = EdukasiTani(
            id_kategori_edu=id_edukasi,
            id_kategori_klasifikasi=id_klasifikasi,
            judul=judul,
            gambar=gambar,
            ringkasan=item.get("ringkasan", ""),
            content=bangun_konten(item),
            referensi=item.get("sumber", []),
        )
        db.add(edukasi_baru)
        print(f"  [INSERT] {judul[:50]}...")

    db.commit()
    print("Seed edukasi_tani selesai.")

# ============================================================
# JALANKAN SEMUA SEED
# ============================================================

def run_seed():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        print("🚀 Mulai seed data...")
        print("-" * 50)
        
        seed_kategori_klasifikasi(db)
        print()
        
        seed_agen_penyebab(db)
        print()
        
        seed_kategori_edukasi(db)
        print()
        
        seed_edukasi_tani(db)
        print()
        
        print("-" * 50)
        print("✅ Semua seed selesai!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()