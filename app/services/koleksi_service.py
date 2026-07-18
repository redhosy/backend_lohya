from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.koleksi_user_model import KoleksiUser
from app.models.edukasi_tani_model import EdukasiTani


def ambil_koleksi_user(db: Session, id_user: int) -> List[dict]:
    koleksi_list = (
        db.query(KoleksiUser)
        .filter(KoleksiUser.id_user == id_user)
        .order_by(KoleksiUser.created_at.desc())
        .all()
    )

    result = []
    for koleksi in koleksi_list:
        edukasi = db.query(EdukasiTani).filter(
            EdukasiTani.id_edukasi == koleksi.id_edukasi
        ).first()

        result.append({
            "id_koleksi": koleksi.id_koleksi,
            "id_user": koleksi.id_user,
            "id_edukasi": koleksi.id_edukasi,
            "created_at": koleksi.created_at,
            "edukasi": {
                "id_edukasi": edukasi.id_edukasi if edukasi else None,
                "judul": edukasi.judul if edukasi else None,
                "gambar": edukasi.gambar if edukasi else None,
                "ringkasan": edukasi.ringkasan if edukasi else None,
                "id_kategori_edu": edukasi.id_kategori_edu if edukasi else None,
                "id_kategori_klasifikasi": edukasi.id_kategori_klasifikasi if edukasi else None,
            } if edukasi else None,
        })

    return result


def tambah_koleksi(db: Session, id_user: int, id_edukasi: int) -> Optional[KoleksiUser]:
    edukasi = db.query(EdukasiTani).filter(
        EdukasiTani.id_edukasi == id_edukasi
    ).first()
    if not edukasi:
        return None

    sudah_ada = db.query(KoleksiUser).filter(
        KoleksiUser.id_user == id_user,
        KoleksiUser.id_edukasi == id_edukasi,
    ).first()
    if sudah_ada:
        return sudah_ada

    koleksi_baru = KoleksiUser(
        id_user=id_user,
        id_edukasi=id_edukasi,
    )
    db.add(koleksi_baru)
    db.commit()
    db.refresh(koleksi_baru)
    return koleksi_baru


def hapus_koleksi(db: Session, id_user: int, id_edukasi: int) -> bool:
    koleksi = db.query(KoleksiUser).filter(
        KoleksiUser.id_user == id_user,
        KoleksiUser.id_edukasi == id_edukasi,
    ).first()
    if not koleksi:
        return False

    db.delete(koleksi)
    db.commit()
    return True


def hapus_semua_koleksi(db: Session, id_user: int) -> int:
    count = db.query(KoleksiUser).filter(
        KoleksiUser.id_user == id_user,
    ).delete()
    db.commit()
    return count


def cek_koleksi(db: Session, id_user: int, id_edukasi: int) -> bool:
    koleksi = db.query(KoleksiUser).filter(
        KoleksiUser.id_user == id_user,
        KoleksiUser.id_edukasi == id_edukasi,
    ).first()
    return koleksi is not None
