from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, selectinload
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi

DISPLAY_NAME_MAP = {
    'daun_bercak': 'Daun Bercak',
    'daun_keriting': 'Daun Keriting',
    'daun_sehat': 'Daun Sehat',
    'non_cabai': 'Non Cabai',
    'non-daun-cabai': 'Non Cabai',
    'bukan_daun_cabai': 'Non Cabai',
}


def ambil_top_kategori(distribusi: Dict[str, float], top_n: int = 2) -> List[Dict[str, Any]]:
    sorted_items = sorted(distribusi.items(), key=lambda x: x[1], reverse=True)
    top_items = sorted_items[:top_n]
    return [{"kode_kelas": k, "skor": v} for k, v in top_items]


def ambil_nama_ilmiah_by_kode(
    db: Session,
    kode_kelas: str
) -> List[str]:
    kategori = (
        db.query(KategoriKlasifikasi)
        .options(selectinload(KategoriKlasifikasi.agen_penyebab_rel))
        .filter(KategoriKlasifikasi.kode_kelas == kode_kelas)
        .first()
    )

    if not kategori:
        return []

    return list(set(r.nama_ilmiah for r in kategori.agen_penyebab_rel))


def gabung_agen_penyebab(
    db: Session,
    top_kategori: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    kode_kelas_list = [item["kode_kelas"] for item in top_kategori]

    kategori_data = (
        db.query(KategoriKlasifikasi)
        .options(selectinload(KategoriKlasifikasi.agen_penyebab_rel))
        .filter(KategoriKlasifikasi.kode_kelas.in_(kode_kelas_list))
        .all()
    )

    kategori_map = {k.kode_kelas: k for k in kategori_data}

    hasil = []
    for item in top_kategori:
        kode = item["kode_kelas"]
        skor = item["skor"]
        kategori = kategori_map.get(kode)

        if kategori:
            nama_kategori = kategori.kategori
            daftar_referensi = [r.nama_ilmiah for r in kategori.agen_penyebab_rel]
        else:
            nama_kategori = kode
            daftar_referensi = []

        hasil.append({
            "kategori": nama_kategori,
            "confidence": skor,
            "referensi": daftar_referensi
        })

    return hasil


def simpan_hasil_klasifikasi(
    db: Session,
    distribusi: Dict[str, float],
    path_gambar: Optional[str] = None,
    id_user: Optional[int] = None
) -> Dict[str, Any]:
    top_kategori = ambil_top_kategori(distribusi)

    kode_utama = top_kategori[0]["kode_kelas"]
    skor_utama = top_kategori[0]["skor"]

    kategori_data = (
        db.query(KategoriKlasifikasi)
        .options(selectinload(KategoriKlasifikasi.agen_penyebab_rel))
        .filter(KategoriKlasifikasi.kode_kelas == kode_utama)
        .first()
    )

    possible_causes = gabung_agen_penyebab(db, top_kategori)
    agen_penyebab = ambil_nama_ilmiah_by_kode(db, kode_utama)

    riwayat = RiwayatKlasifikasi(
        id_user=id_user,
        id_kategori=kategori_data.id_kategori if kategori_data else None,
        kategori=kategori_data.kategori if kategori_data else DISPLAY_NAME_MAP.get(kode_utama, kode_utama),
        skor_keyakinan=skor_utama,
        path_gambar=path_gambar,
        distribusi_probabilitas=distribusi,
    )

    db.add(riwayat)
    db.commit()
    db.refresh(riwayat)

    return {
        "id_riwayat": riwayat.id_riwayat,
        "kategori": riwayat.kategori,
        "kode_kelas": kode_utama,
        "confidence_score": riwayat.skor_keyakinan,
        "distribution": riwayat.distribusi_probabilitas,
        "possible_causes": possible_causes,
        "agen_penyebab": agen_penyebab,
        "deskripsi": kategori_data.deskripsi if kategori_data else None,
        "perawatan": kategori_data.perawatan if kategori_data else None,
        "pencegahan": kategori_data.pencegahan if kategori_data else None,
        "referensi": kategori_data.referensi if kategori_data else None,
    }


def ambil_riwayat_klasifikasi(
    db: Session,
    id_user: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> List[RiwayatKlasifikasi]:
    query = db.query(RiwayatKlasifikasi).options(
        selectinload(RiwayatKlasifikasi.kategori_rel).selectinload(KategoriKlasifikasi.agen_penyebab_rel)
    )

    if id_user:
        query = query.filter(RiwayatKlasifikasi.id_user == id_user)

    riwayat_list = query.order_by(RiwayatKlasifikasi.created_at.desc()).offset(offset).limit(limit).all()

    return riwayat_list


def ambil_riwayat_by_id(db: Session, id_riwayat: int) -> Optional[RiwayatKlasifikasi]:
    riwayat = (
        db.query(RiwayatKlasifikasi)
        .options(
            selectinload(RiwayatKlasifikasi.kategori_rel).selectinload(KategoriKlasifikasi.agen_penyebab_rel)
        )
        .filter(RiwayatKlasifikasi.id_riwayat == id_riwayat)
        .first()
    )
    return riwayat


def hapus_riwayat(db: Session, id_riwayat: int) -> bool:
    riwayat = db.query(RiwayatKlasifikasi).filter(RiwayatKlasifikasi.id_riwayat == id_riwayat).first()
    if not riwayat:
        return False
    db.delete(riwayat)
    db.commit()
    return True


def hapus_semua_riwayat(db: Session, id_user: Optional[int] = None) -> int:
    query = db.query(RiwayatKlasifikasi)
    if id_user:
        query = query.filter(RiwayatKlasifikasi.id_user == id_user)
    count = query.delete()
    db.commit()
    return count
