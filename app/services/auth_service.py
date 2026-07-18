from typing import Optional
from datetime import datetime
from fastapi import HTTPException
from app.auth.google_auth import verify_google_token
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token, create_reset_token, decode_reset_token
from app.services.otp_service import buat_otp, verifikasi_otp, verifikasi_otp_by_email
from app.services.email_service import kirim_otp_email


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def register_user(db: Session, payload) -> dict:
    existing = get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email sudah terdaftar",
        )

    hashed = hash_password(payload.password)

    new_user = User(
        nama=payload.nama,
        email=payload.email,
        password_hash=hashed,
        auth_provider="local",
        is_verified=False,
    )

    user = create_user(db, new_user)

    otp_code = buat_otp(db, user.id_user, user.email, purpose="register")

    try:
        await kirim_otp_email(user.email, otp_code)
    except Exception:
        pass

    return {
        "message": "Registrasi berhasil. Silakan verifikasi OTP yang dikirim ke email Anda.",
        "user_id": user.id_user,
    }


async def verify_register_otp(db: Session, payload) -> dict:
    user = get_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User sudah terverifikasi",
        )

    valid = verifikasi_otp(db, user.id_user, payload.otp, purpose="register")
    if not valid:
        raise HTTPException(
            status_code=400,
            detail="OTP tidak valid atau sudah kedaluwarsa",
        )

    user.is_verified = True
    db.commit()

    return {"message": "Verifikasi berhasil"}


async def resend_otp_user(db: Session, payload) -> dict:
    user = get_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User sudah terverifikasi",
        )

    otp_code = buat_otp(db, user.id_user, user.email, purpose="register")

    try:
        await kirim_otp_email(user.email, otp_code)
    except Exception:
        pass

    return {"message": "OTP baru telah dikirim ke email Anda."}


async def login_user(db: Session, payload) -> dict:
    user = get_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Password salah",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Akun belum diverifikasi. Silakan verifikasi OTP terlebih dahulu.",
        )

    user.last_login = datetime.utcnow()

    access_token = create_access_token(user.id_user)
    refresh_token = create_refresh_token(user.id_user)
    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id_user": user.id_user,
            "nama": user.nama,
            "email": user.email,
        },
    }

async def google_login_user(db: Session, payload) -> dict:
    google_user = await verify_google_token(payload.id_token)

    # 1. Cari berdasarkan google_id terlebih dahulu
    user = get_by_google_id(db, google_user["google_id"])

    # 2. Jika tidak ketemu, cari berdasarkan email
    if not user:
        user = get_by_email(db, google_user["email"])

        # 3. Jika user ditemukan via email tapi belum punya google_id, update
        if user and not user.google_id:
            user.google_id = google_user["google_id"]

    # 4. Jika tetap tidak ketemu, buat user baru
    if not user:
        new_user = User(
            nama=google_user["name"],
            email=google_user["email"],
            password_hash="",
            auth_provider="google",
            is_verified=True,
            profile_image_url=google_user.get("picture"),
            google_id=google_user["google_id"],
        )
        user = create_user(db, new_user)

    user.last_login = datetime.utcnow()

    access_token = create_access_token(user.id_user)
    refresh_token = create_refresh_token(user.id_user)
    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id_user": user.id_user,
            "nama": user.nama,
            "email": user.email,
        },
    }

async def get_forgot_password_otp(db: Session, payload) -> dict:
    user = get_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    otp_code = buat_otp(db, user.id_user, user.email, purpose="forgot_password")

    try:
        await kirim_otp_email(user.email, otp_code)
    except Exception:
        pass

    return {"message": "OTP untuk reset password telah dikirim ke email Anda."}


async def verify_reset_otp(db: Session, payload) -> dict:
    otp_record = verifikasi_otp_by_email(
        db, 
        payload.email, 
        payload.otp, 
        purpose="forgot_password"
    )
    
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="OTP tidak valid atau sudah kedaluwarsa",
        )

    # Mark OTP as used
    otp_record.is_used = True
    db.commit()

    # Generate reset token
    reset_token = create_reset_token(payload.email)

    return {
        "message": "OTP valid. Gunakan reset token untuk mengubah password.",
        "reset_token": reset_token,
    }


async def reset_password(db: Session, payload) -> dict:
    # Decode reset token to get email
    email = decode_reset_token(payload.reset_token)
    if not email or email != payload.email:
        raise HTTPException(
            status_code=400,
            detail="Reset token tidak valid atau sudah kedaluwarsa",
        )

    user = get_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    # Verify password not same as old
    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Password baru tidak boleh sama dengan password lama",
        )

    hashed = hash_password(payload.new_password)
    user.password_hash = hashed
    db.commit()

    return {"message": "Password berhasil direset."}


async def change_password(db: Session, user_id: int, payload) -> dict:
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    # Verify old password
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Password lama salah",
        )

    # Verify new password not same as old
    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Password baru tidak boleh sama dengan password lama",
        )

    # Verify confirm password matches
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Konfirmasi password tidak cocok",
        )

    hashed = hash_password(payload.new_password)
    user.password_hash = hashed
    db.commit()

    return {"message": "Password berhasil diubah."}


async def refresh_access_token(db: Session, payload) -> dict:
    user_id = decode_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Refresh token tidak valid atau sudah kedaluwarsa",
        )

    user = db.query(User).filter(User.id_user == user_id).first()
    if not user or user.refresh_token != payload.refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token tidak valid",
        )

    # Generate new tokens
    new_access_token = create_access_token(user.id_user)
    new_refresh_token = create_refresh_token(user.id_user)
    user.refresh_token = new_refresh_token
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id_user": user.id_user,
            "nama": user.nama,
            "email": user.email,
        },
    }


async def logout_user(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan",
        )

    user.refresh_token = None
    db.commit()

    return {"message": "Logout berhasil"}
