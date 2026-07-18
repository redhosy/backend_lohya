from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp_verification_model import OtpVerification
from app.auth.otp_generator import generate_otp


OTP_EXPIRE_MINUTES = 5


def buat_otp(db: Session, user_id: int, email: str, purpose: str = "register") -> str:
    otp_code = generate_otp()
    expired_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    otp_record = OtpVerification(
        user_id=user_id,
        email=email,
        otp_code=otp_code,
        purpose=purpose,
        expired_at=expired_at,
    )
    db.add(otp_record)
    db.commit()

    return otp_code


def verifikasi_otp(db: Session, user_id: int, otp_code: str, purpose: str = "register") -> bool:
    otp_record = (
        db.query(OtpVerification)
        .filter(
            OtpVerification.user_id == user_id,
            OtpVerification.otp_code == otp_code,
            OtpVerification.purpose == purpose,
            OtpVerification.is_used == False,
            OtpVerification.expired_at > datetime.utcnow(),
        )
        .order_by(OtpVerification.created_at.desc())
        .first()
    )

    if not otp_record:
        return False

    otp_record.is_used = True
    db.commit()

    return True


def verifikasi_otp_by_email(db: Session, email: str, otp_code: str, purpose: str) -> OtpVerification | None:
    otp_record = (
        db.query(OtpVerification)
        .filter(
            OtpVerification.email == email,
            OtpVerification.otp_code == otp_code,
            OtpVerification.purpose == purpose,
            OtpVerification.is_used == False,
            OtpVerification.expired_at > datetime.utcnow(),
        )
        .order_by(OtpVerification.created_at.desc())
        .first()
    )

    if not otp_record:
        return None

    return otp_record
