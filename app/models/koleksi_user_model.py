from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class KoleksiUser(Base):
    __tablename__ = "koleksi_user"

    id_koleksi = Column( Integer, primary_key=True, autoincrement=True,)
    id_user = Column( Integer, ForeignKey("users.id_user", ondelete="CASCADE",), nullable=False, index=True,)
    id_edukasi = Column( Integer, ForeignKey("edukasi_tani.id_edukasi", ondelete="CASCADE",), nullable=False, index=True,)
    created_at = Column( DateTime(timezone=True), server_default=func.now(),)