from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.edukasi_tani_model import EdukasiTani


def ambil_semua_edukasi(db: Session, id_kategori_edu: Optional[int] = None) -> List[EdukasiTani]:
    query = db.query(EdukasiTani)
    if id_kategori_edu is not None:
        query = query.filter(EdukasiTani.id_kategori_edu == id_kategori_edu)
    return query.order_by(EdukasiTani.created_at.desc()).all()


def ambil_edukasi_by_id(db: Session, id_edukasi: int) -> Optional[EdukasiTani]:
    return db.query(EdukasiTani).filter(EdukasiTani.id_edukasi == id_edukasi).first()


def ambil_edukasi_by_kategori(db: Session, id_kategori_edu: int) -> List[EdukasiTani]:
    return (
        db.query(EdukasiTani)
        .filter(EdukasiTani.id_kategori_edu == id_kategori_edu)
        .order_by(EdukasiTani.created_at.desc())
        .all()
    )


def buat_edukasi(db: Session, data: dict) -> EdukasiTani:
    edukasi = EdukasiTani(**data)
    db.add(edukasi)
    db.commit()
    db.refresh(edukasi)
    return edukasi


def update_edukasi(db: Session, id_edukasi: int, data: dict) -> Optional[EdukasiTani]:
    edukasi = db.query(EdukasiTani).filter(EdukasiTani.id_edukasi == id_edukasi).first()
    if not edukasi:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(edukasi, key, value)
    db.commit()
    db.refresh(edukasi)
    return edukasi


def hapus_edukasi(db: Session, id_edukasi: int) -> bool:
    edukasi = db.query(EdukasiTani).filter(EdukasiTani.id_edukasi == id_edukasi).first()
    if not edukasi:
        return False
    db.delete(edukasi)
    db.commit()
    return True
