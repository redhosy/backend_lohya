import os
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.auth_schema import ProfileResponse
from app.services.profile_service import update_profile

router = APIRouter()

UPLOAD_DIR = "uploads/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/profile", response_model=ProfileResponse)
def get_profile_endpoint(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/profile", response_model=ProfileResponse)
def edit_profile_endpoint(
    nama: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        image_url = None
        if profile_image:
            ext = os.path.splitext(profile_image.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(profile_image.file.read())
            image_url = f"/{UPLOAD_DIR}/{filename}"

        return update_profile(
            db,
            current_user.id_user,
            nama=nama,
            email=email,
            profile_image_url=image_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal update profile: {str(e)}",
        )


@router.post("/auth/logout")
def logout_endpoint(
    current_user: User = Depends(get_current_user),
):
    return {"message": "Logout berhasil"}
