from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class RiwayatKlasifikasi(Base):
    __tablename__ = "riwayat_klasifikasi"

    id_riwayat = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=True, index=True)
    id_kategori = Column(Integer, ForeignKey("kategori_klasifikasi.id_kategori"), nullable=True, index=True)
    kategori = Column(String(100), nullable=False)
    skor_keyakinan = Column(Float, nullable=False)
    distribusi_probabilitas = Column(JSON, nullable=True)
    path_gambar = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kategori_rel = relationship("KategoriKlasifikasi", back_populates="riwayat_klasifikasi_rel", lazy="selectin")
    user = relationship("User", back_populates="riwayat_klasifikasi_rel")

    @property
    def kode_kelas(self) -> str:
        if self.kategori_rel:
            return self.kategori_rel.kode_kelas
        return ''

    __table_args__ = (
        Index("idx_riwayat_id_kategori", "id_kategori"),
    )
