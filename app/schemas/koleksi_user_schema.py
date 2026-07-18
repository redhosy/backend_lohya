from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KoleksiBuat(BaseModel):
    id_user: int
    id_edukasi: int


class EdukasiDalamKoleksi(BaseModel):
    id_edukasi: int
    judul: Optional[str] = None
    gambar: Optional[str] = None
    ringkasan: Optional[str] = None
    id_kategori_edu: Optional[int] = None
    id_kategori_klasifikasi: Optional[int] = None


class KoleksiUserResponse(BaseModel):
    id_koleksi: int
    id_user: int
    id_edukasi: int
    created_at: datetime
    edukasi: Optional[EdukasiDalamKoleksi] = None

    class Config:
        from_attributes = True


class KoleksiStatusResponse(BaseModel):
    is_bookmarked: bool