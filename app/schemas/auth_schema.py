from typing import Optional
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nama: str
    email: EmailStr
    password: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResendOtpRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class GoogleLoginRequest(BaseModel):
    id_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

class VerifyResetOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class UserResponse(BaseModel):
    id_user: int
    nama: str
    email: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ProfileResponse(BaseModel):
    id_user: int
    nama: str
    email: str
    profile_image_url: Optional[str] = None
    auth_provider: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True


class EditProfileRequest(BaseModel):
    nama: Optional[str] = None
    email: Optional[str] = None
    profile_image_url: Optional[str] = None
