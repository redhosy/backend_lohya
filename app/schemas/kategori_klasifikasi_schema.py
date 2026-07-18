from typing import List, Optional
from pydantic import BaseModel

from app.schemas.agen_penyebab_schema import AgenPenyebabRespon

class KategoriKlasifikasiBuat(BaseModel):
    kode_kelas: str
    kategori: str
    deskripsi: Optional[str] = None
    perawatan: Optional[List[str]] = None
    pencegahan: Optional[List[str]] = None
    referensi: Optional[List[dict]] = None
    is_default: bool = False


class KategoriKlasifikasiRespon(BaseModel):
    id_kategori: int
    kode_kelas: str
    kategori: str

    deskripsi: Optional[str] = None
    perawatan: Optional[List[str]] = None
    pencegahan: Optional[List[str]] = None
    referensi: Optional[List[dict]] = None
    is_default: bool
    agen_penyebab_rel: List[AgenPenyebabRespon] = []

    class Config:
        from_attributes = True
