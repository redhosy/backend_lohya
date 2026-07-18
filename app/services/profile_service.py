from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user_model import User


def ambil_profile(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )
    return user


def update_profile(
    db: Session,
    user_id: int,
    nama: Optional[str] = None,
    email: Optional[str] = None,
    profile_image_url: Optional[str] = None,
) -> User:
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    if nama is not None:
        user.nama = nama
    if email is not None:
        existing = db.query(User).filter(User.email == email, User.id_user != user_id).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email sudah digunakan oleh akun lain",
            )
        user.email = email
    if profile_image_url is not None:
        user.profile_image_url = profile_image_url

    db.commit()
    db.refresh(user)

    return user
