from datetime import datetime
import enum

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class StatusLaporan(str, enum.Enum):
    pending = "pending"
    dibaca = "dibaca"


class LaporanBaru(Base):
    __tablename__ = "laporan_baru"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id_user"), nullable=False)
    foto_url: Mapped[str] = mapped_column(String(500), nullable=False)
    deskripsi_masalah: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(StatusLaporan, native_enum=False, length=20),
        default=StatusLaporan.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="laporans")
