from sqlalchemy import Column, Integer, String
from app.db.database import Base


class KategoriEdukasi(Base):
    __tablename__ = "kategori_edukasi"

    id_kategori_edu = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nama_kategori_edu = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    def __str__(self):
        return self.nama_kategori_edu