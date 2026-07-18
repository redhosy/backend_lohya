from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyOtpRequest,
    VerifyResetOtpRequest,
    ResendOtpRequest,
    LoginRequest,
    LoginResponse,
    ChangePasswordRequest,
    GoogleLoginRequest,
    RefreshTokenRequest,
)
from app.services.auth_service import (
    get_forgot_password_otp,
    register_user,
    reset_password,
    verify_register_otp,
    verify_reset_otp,
    resend_otp_user,
    login_user,
    change_password,
    google_login_user,
    refresh_access_token,
    logout_user,
)

router = APIRouter()


@router.post("/auth/register")
async def register_endpoint(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        return await register_user(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal registrasi: {str(e)}",
        )


@router.post("/auth/verify-register-otp")
async def verify_register_otp_endpoint(
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db),
):
    try:
        return await verify_register_otp(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal verifikasi OTP: {str(e)}",
        )


@router.post("/auth/resend-otp")
async def resend_otp_endpoint(
    payload: ResendOtpRequest,
    db: Session = Depends(get_db),
):
    try:
        return await resend_otp_user(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengirim ulang OTP: {str(e)}",
        )


@router.post("/auth/login", response_model=LoginResponse)
async def login_endpoint(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return await login_user(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal login: {str(e)}",
        )
        
@router.post("/auth/google-login", response_model=LoginResponse)
async def google_login_endpoint(
    payload: GoogleLoginRequest,
    db:Session = Depends(get_db),
):
    try:
        return await google_login_user(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal login dengan Google: {str(e)}",
        )

@router.post("/auth/forgot-password")
async def forgot_password_endpoint(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return await get_forgot_password_otp(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memproses permintaan lupa password: {str(e)}",
        )


@router.post("/auth/verify-reset-otp")
async def verify_reset_otp_endpoint(
    payload: VerifyResetOtpRequest,
    db: Session = Depends(get_db),
):
    try:
        return await verify_reset_otp(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal verifikasi OTP reset: {str(e)}",
        )


@router.post("/auth/reset-password")
async def reset_password_endpoint(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return await reset_password(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mereset password: {str(e)}",
        )


@router.put("/auth/change-password")
async def change_password_endpoint(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        return await change_password(db, current_user.id_user, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengubah password: {str(e)}",
        )


@router.post("/auth/refresh", response_model=LoginResponse)
async def refresh_token_endpoint(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        return await refresh_access_token(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal refresh token: {str(e)}",
        )


@router.post("/auth/logout")
async def logout_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        return await logout_user(db, current_user.id_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal logout: {str(e)}",
        )