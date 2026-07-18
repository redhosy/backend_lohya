from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.laporan_baru import LaporanBaru
from app.models.user_model import User
from app.schemas.laporan import LaporanResponse
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.services.image import save_image_and_create_thumbnail
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/laporan", tags=["Laporan"])


@router.post("", response_model=LaporanResponse, status_code=status.HTTP_201_CREATED)
async def create_laporan(
    deskripsi_masalah: str = Form(...),
    foto: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await foto.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file melebihi batas 5MB")

    image_url, thumbnail_url = await save_image_and_create_thumbnail(
        content, foto.filename, subfolder="laporan"
    )

    laporan = LaporanBaru(
        user_id=current_user.id_user,
        foto_url=image_url,
        deskripsi_masalah=deskripsi_masalah,
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


@router.get("", response_model=list[LaporanResponse])
def get_my_laporans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(LaporanBaru)
        .where(LaporanBaru.user_id == current_user.id_user)
        .order_by(LaporanBaru.created_at.desc())
    )
    return result.scalars().all()
