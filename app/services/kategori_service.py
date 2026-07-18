from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi


def ambil_semua_kategori(db: Session) -> List[KategoriKlasifikasi]:
    return (
        db.query(KategoriKlasifikasi)
        .options(selectinload(KategoriKlasifikasi.agen_penyebab_rel))
        .all()
    )


def ambil_kategori_by_kode(db: Session, kode_kelas: str) -> Optional[KategoriKlasifikasi]:
    return (
        db.query(KategoriKlasifikasi)
        .options(selectinload(KategoriKlasifikasi.agen_penyebab_rel))
        .filter(KategoriKlasifikasi.kode_kelas == kode_kelas)
        .first()
    )


def ambil_kategori_dict_by_kode(db: Session, kode_kelas: str) -> Optional[Dict[str, Any]]:
    kategori = ambil_kategori_by_kode(db, kode_kelas)
    if not kategori:
        return None

    return {
        "id_kategori": kategori.id_kategori,
        "kode_kelas": kategori.kode_kelas,
        "kategori": kategori.kategori,
        "deskripsi": kategori.deskripsi,
        "perawatan": kategori.perawatan,
        "pencegahan": kategori.pencegahan,
        "agen_penyebab": [
            r.nama_ilmiah for r in kategori.agen_penyebab_rel
        ],
    }
