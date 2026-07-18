from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class EdukasiTaniBuat(BaseModel):
    id_kategori_edu: int
    id_kategori_klasifikasi: Optional[int] = None
    
    judul: str
    gambar: Optional[str] = None
    ringkasan: Optional[str] = None
    content: str
    refrensi: Optional[list] = None
    
class EdukasiTaniUpdate(BaseModel):
    judul: Optional[str] = None
    gambar: Optional[str] = None
    ringkasan: Optional[str] = None
    content: Optional[str] = None
    referensi: Optional[list] = None


class EdukasiTaniRespon(BaseModel):
    id_edukasi: int
    id_kategori_edu: int
    id_kategori_klasifikasi: Optional[int] = None
    
    judul: str
    gambar: Optional[str] = None
    ringkasan: Optional[str] = None
    content: str
    referensi: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True



