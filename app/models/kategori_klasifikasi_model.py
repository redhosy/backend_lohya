from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class KategoriKlasifikasi(Base):
    __tablename__ = "kategori_klasifikasi"

    id_kategori = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kode_kelas = Column(String(50), unique=True, nullable=False, index=True)
    kategori = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=True)
    perawatan = Column(JSON, nullable=True)
    pencegahan = Column(JSON, nullable=True)
    referensi = Column(JSON, nullable=True)
    edukasi_id = Column(Integer, nullable=True)
    is_default = Column(Boolean, default=False)

    agen_penyebab_rel = relationship("AgenPenyebab", back_populates="kategori_rel", lazy="selectin")
    riwayat_klasifikasi_rel = relationship("RiwayatKlasifikasi", back_populates="kategori_rel", lazy="selectin")

    def __str__(self):
        return self.kategori
