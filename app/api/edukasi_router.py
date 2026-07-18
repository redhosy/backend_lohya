from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.edukasi_tani_schema import (
    EdukasiTaniBuat,
    EdukasiTaniRespon,
    EdukasiTaniUpdate,
)
from app.services.edukasi_service import (
    ambil_semua_edukasi,
    ambil_edukasi_by_id,
    ambil_edukasi_by_kategori,
    buat_edukasi,
    update_edukasi,
    hapus_edukasi,
)

router = APIRouter()


@router.get("/edukasi", response_model=List[EdukasiTaniRespon])
def ambil_semua_edukasi_endpoint(
    id_kategori_edu: Optional[int] = Query(None, description="Filter berdasarkan ID kategori edukasi"),
    db: Session = Depends(get_db),
):
    try:
        return ambil_semua_edukasi(db, id_kategori_edu=id_kategori_edu)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat edukasi: {str(e)}")


@router.get("/edukasi/{id_edukasi}", response_model=EdukasiTaniRespon)
def ambil_edukasi_by_id_endpoint(id_edukasi: int, db: Session = Depends(get_db)):
    try:
        edukasi = ambil_edukasi_by_id(db, id_edukasi)
        if not edukasi:
            raise HTTPException(status_code=404, detail="Edukasi tidak ditemukan")
        return edukasi
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat edukasi: {str(e)}")


@router.get("/edukasi/kategori/{id_kategori_edu}", response_model=List[EdukasiTaniRespon])
def ambil_edukasi_by_kategori_endpoint(id_kategori_edu: int, db: Session = Depends(get_db)):
    try:
        edukasi_list = ambil_edukasi_by_kategori(db, id_kategori_edu)
        if not edukasi_list:
            raise HTTPException(status_code=404, detail=f"Edukasi dengan kategori ID '{id_kategori_edu}' tidak ditemukan")
        return edukasi_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat edukasi: {str(e)}")


@router.post("/edukasi", response_model=EdukasiTaniRespon)
def buat_edukasi_endpoint(data: EdukasiTaniBuat, db: Session = Depends(get_db)):
    try:
        return buat_edukasi(db, data.model_dump())
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal membuat edukasi: {str(e)}")


@router.put("/edukasi/{id_edukasi}", response_model=EdukasiTaniRespon)
def update_edukasi_endpoint(id_edukasi: int, data: EdukasiTaniUpdate, db: Session = Depends(get_db)):
    try:
        edukasi = update_edukasi(db, id_edukasi, data.model_dump(exclude_unset=True))
        if not edukasi:
            raise HTTPException(status_code=404, detail="Edukasi tidak ditemukan")
        return edukasi
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal mengupdate edukasi: {str(e)}")


@router.delete("/edukasi/{id_edukasi}")
def hapus_edukasi_endpoint(id_edukasi: int, db: Session = Depends(get_db)):
    try:
        berhasil = hapus_edukasi(db, id_edukasi)
        if not berhasil:
            raise HTTPException(status_code=404, detail="Edukasi tidak ditemukan")
        return {"message": "Edukasi berhasil dihapus"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menghapus edukasi: {str(e)}")
