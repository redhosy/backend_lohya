from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.kategori_klasifikasi_schema import KategoriKlasifikasiRespon
from app.services.kategori_service import (
    ambil_semua_kategori,
    ambil_kategori_by_kode,
)

router = APIRouter()


@router.get("/kategori-klasifikasi", response_model=List[KategoriKlasifikasiRespon])
def ambil_semua_kategori_endpoint(db: Session = Depends(get_db)):
    try:
        return ambil_semua_kategori(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat kategori: {str(e)}"
        )


@router.get("/kategori-klasifikasi/{kode_kelas}", response_model=KategoriKlasifikasiRespon)
def ambil_kategori_by_kode_endpoint(kode_kelas: str, db: Session = Depends(get_db)):
    try:
        kategori = ambil_kategori_by_kode(db, kode_kelas)
        if not kategori:
            raise HTTPException(
                status_code=404,
                detail=f"Kategori '{kode_kelas}' tidak ditemukan"
            )
        return kategori
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat kategori: {str(e)}"
        )
