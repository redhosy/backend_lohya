from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.sql import func
from app.db.database import Base


class OtpVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id_user"),
        nullable=False,
    )
    email = Column(String(255), nullable=False)
    otp_code = Column(String(5), nullable=False)
    purpose = Column(String(20), nullable=False, default="register")  # register / forgot_password
    expired_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
