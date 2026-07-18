from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=True)
    nama = Column(String(100), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    auth_provider = Column(String(20), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    riwayat_klasifikasi_rel = relationship("RiwayatKlasifikasi", back_populates="user",cascade="all, delete-orphan", lazy="selectin")
    laporans = relationship("LaporanBaru", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    @hybrid_property
    def total_scan(self):
        return len(self.riwayat_klasifikasi_rel) if self.riwayat_klasifikasi_rel else 0