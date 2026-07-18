import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.edukasi_tani_model import EdukasiTani
from app.models.kategori_edukasi_model import KategoriEdukasi


DATA_DIR = Path(__file__).parent.parent / "data"


def bangun_konten(item: dict) -> str:
    bagian = []
    for isi in item.get("isi", []):
        subjudul = isi.get("subjudul", "")
        konten = isi.get("konten", "")
        if subjudul:
            bagian.append(f"↪ {subjudul}\n\n{konten}")
        else:
            bagian.append(konten)

    tips = item.get("tips_lapangan", [])
    if tips:
        bagian.append("✓ Tips Lapangan")
        for i, tip in enumerate(tips, 1):
            bagian.append(f"{i}. {tip}")

    catatan = item.get("catatan")
    if catatan:
        bagian.append(f"‼ Catatan\n\n{catatan}")

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
    json_path = DATA_DIR / "edukasi_metadata.json"
    with open(json_path, "r", encoding="utf-8") as f:
        daftar_edukasi = json.load(f)

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


def run_seed():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        print("Mulai seed edukasi...")
        seed_edukasi_tani(db)
        print("Seed edukasi selesai!")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
