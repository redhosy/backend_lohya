from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, model_validator

class PossibleCauseItem(BaseModel):
    kategori: str
    confidence: float
    referensi: List[str]

class SimpanHasilBuat(BaseModel):
    distribusi_probabilitas: dict
    id_user: Optional[int] = None


class SimpanHasilRespon(BaseModel):
    id_riwayat: int
    kategori: str
    kode_kelas: Optional[str] = None
    confidence_score: float
    distribution: dict
    possible_causes: List[PossibleCauseItem]
    agen_penyebab: List[str] = []
    deskripsi: Optional[str] = None
    perawatan: Optional[List[str]] = None
    pencegahan: Optional[List[str]] = None
    referensi: Optional[List[dict]] = None

    class Config:
        from_attributes = True

# RIWAYAT KLASIFIKASI

class RiwayatKlasifikasiRespon(BaseModel):
    id_riwayat: int
    id_user: Optional[int] = None
    id_kategori: Optional[int] = None

    kategori: str
    kode_kelas: Optional[str] = None
    skor_keyakinan: float
    path_gambar: Optional[str] = None
    distribusi_probabilitas: Optional[dict] = None
    agen_penyebab: Optional[List[str]] = None
    deskripsi: Optional[str] = None
    perawatan: Optional[List[str]] = None
    pencegahan: Optional[List[str]] = None
    referensi: Optional[List[dict]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def populate_from_rel(cls, data):
        kategori_rel = getattr(data, "kategori_rel", None)
        if kategori_rel:
            if not getattr(data, "kode_kelas", None):
                data.kode_kelas = kategori_rel.kode_kelas
            if not getattr(data, "deskripsi", None):
                data.deskripsi = kategori_rel.deskripsi
            if not getattr(data, "perawatan", None):
                data.perawatan = kategori_rel.perawatan
            if not getattr(data, "pencegahan", None):
                data.pencegahan = kategori_rel.pencegahan
            if not getattr(data, "referensi", None):
                data.referensi = kategori_rel.referensi
            agen_rel = getattr(kategori_rel, "agen_penyebab_rel", None)
            if agen_rel and not getattr(data, "agen_penyebab", None):
                data.agen_penyebab = [r.nama_ilmiah for r in agen_rel]
        return data