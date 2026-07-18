from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship


class EdukasiTani(Base):
    __tablename__ = "edukasi_tani"

    id_edukasi = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_kategori_klasifikasi = Column(Integer, ForeignKey("kategori_klasifikasi.id_kategori"), nullable=True, index=True)
    id_kategori_edu = Column(Integer, ForeignKey("kategori_edukasi.id_kategori_edu"), nullable=False, index=True)
    judul = Column(String(255), nullable=False)
    gambar = Column(String(500), nullable=True)
    ringkasan = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    referensi = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    kategori_edu_rel = relationship("KategoriEdukasi", backref="edukasi_tani_rel", lazy="selectin")
    kategori_klasifikasi_rel = relationship("KategoriKlasifikasi", backref="edukasi_tani_rel", lazy="selectin")
