from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.koleksi_user_schema import (
    KoleksiBuat,
    KoleksiUserResponse,
    KoleksiStatusResponse,
)
from app.services.koleksi_service import (
    ambil_koleksi_user,
    tambah_koleksi,
    hapus_koleksi,
    hapus_semua_koleksi,
    cek_koleksi,
)

router = APIRouter()


@router.get("/koleksi", response_model=List[KoleksiUserResponse])
def ambil_koleksi_endpoint(
    id_user: int = Query(..., description="ID user"),
    db: Session = Depends(get_db),
):
    try:
        return ambil_koleksi_user(db, id_user)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat koleksi: {str(e)}",
        )


@router.get("/koleksi/status", response_model=KoleksiStatusResponse)
def cek_koleksi_endpoint(
    id_user: int = Query(..., description="ID user"),
    id_edukasi: int = Query(..., description="ID edukasi"),
    db: Session = Depends(get_db),
):
    try:
        is_bookmarked = cek_koleksi(db, id_user, id_edukasi)
        return {"is_bookmarked": is_bookmarked}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengecek koleksi: {str(e)}",
        )


@router.post("/koleksi", response_model=KoleksiUserResponse)
def tambah_koleksi_endpoint(
    data: KoleksiBuat,
    db: Session = Depends(get_db),
):
    try:
        koleksi = tambah_koleksi(db, data.id_user, data.id_edukasi)
        if not koleksi:
            raise HTTPException(
                status_code=404,
                detail="Edukasi tidak ditemukan",
            )
        return koleksi
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menambah koleksi: {str(e)}",
        )


@router.delete("/koleksi")
def hapus_koleksi_endpoint(
    id_user: int = Query(..., description="ID user"),
    id_edukasi: int = Query(..., description="ID edukasi"),
    db: Session = Depends(get_db),
):
    try:
        berhasil = hapus_koleksi(db, id_user, id_edukasi)
        if not berhasil:
            raise HTTPException(
                status_code=404,
                detail="Koleksi tidak ditemukan",
            )
        return {"message": "Koleksi berhasil dihapus"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus koleksi: {str(e)}",
        )


@router.delete("/koleksi/all")
def hapus_semua_koleksi_endpoint(
    id_user: int = Query(..., description="ID user"),
    db: Session = Depends(get_db),
):
    try:
        count = hapus_semua_koleksi(db, id_user)
        return {"message": f"{count} koleksi berhasil dihapus"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus semua koleksi: {str(e)}",
        )
