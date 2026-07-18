from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class AgenPenyebab(Base):
    __tablename__ = "agen_penyebab"

    id_agen = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_kategori = Column(Integer, ForeignKey("kategori_klasifikasi.id_kategori"), nullable=False, index=True)
    nama_ilmiah = Column(String(255), nullable=False)
    jenis = Column(String(50), nullable=False)

    kategori_rel = relationship("KategoriKlasifikasi", back_populates="agen_penyebab_rel")

    def __str__(self):
        return f"{self.nama_ilmiah} ({self.jenis})"

    __table_args__ = (
        Index("idx_agen_id_kategori", "id_kategori"),
    )
