import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.riwayat_klasifikasi_schema import (
    SimpanHasilRespon,
    RiwayatKlasifikasiRespon,
)
from app.services.simpan_hasil_service import (
    simpan_hasil_klasifikasi,
    ambil_riwayat_klasifikasi,
    ambil_riwayat_by_id,
    hapus_riwayat,
    hapus_semua_riwayat,
)

router = APIRouter()

UPLOAD_DIR = "uploads/hasil"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/simpan-hasil", response_model=SimpanHasilRespon)
def simpan_hasil_endpoint(
    distribusi_probabilitas: str = Form(...),
    id_user: Optional[int] = Form(None),
    gambar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        distribusi = json.loads(distribusi_probabilitas)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="distribusi_probabilitas harus berupa JSON string yang valid.")

    if not distribusi:
        raise HTTPException(status_code=400, detail="Distribusi probabilitas tidak boleh kosong.")

    try:
        path_gambar = None
        if gambar:
            ext = os.path.splitext(gambar.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(gambar.file.read())
            path_gambar = f"/{UPLOAD_DIR}/{filename}"

        hasil = simpan_hasil_klasifikasi(
            db=db,
            distribusi=distribusi,
            path_gambar=path_gambar,
            id_user=id_user,
        )
        return hasil

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan hasil klasifikasi: {str(e)}")


@router.get("/riwayat-klasifikasi", response_model=List[RiwayatKlasifikasiRespon])
def ambil_riwayat_endpoint(
    id_user: Optional[int] = Query(None, description="Filter berdasarkan ID user"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        riwayat_list = ambil_riwayat_klasifikasi(db, id_user=id_user, limit=limit, offset=offset)
        return riwayat_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat riwayat: {str(e)}")


@router.get("/riwayat-klasifikasi/{id_riwayat}", response_model=RiwayatKlasifikasiRespon)
def ambil_riwayat_by_id_endpoint(id_riwayat: int, db: Session = Depends(get_db)):
    try:
        riwayat = ambil_riwayat_by_id(db, id_riwayat)
        if not riwayat:
            raise HTTPException(status_code=404, detail="Riwayat tidak ditemukan")
        return riwayat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat riwayat: {str(e)}")


@router.delete("/riwayat-klasifikasi/{id_riwayat}")
def hapus_riwayat_endpoint(id_riwayat: int, db: Session = Depends(get_db)):
    try:
        berhasil = hapus_riwayat(db, id_riwayat)
        if not berhasil:
            raise HTTPException(status_code=404, detail="Riwayat tidak ditemukan")
        return {"message": "Riwayat berhasil dihapus"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menghapus riwayat: {str(e)}")


@router.delete("/riwayat-klasifikasi")
def hapus_semua_riwayat_endpoint(
    id_user: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        count = hapus_semua_riwayat(db, id_user=id_user)
        return {"message": f"{count} riwayat berhasil dihapus"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menghapus riwayat: {str(e)}")
