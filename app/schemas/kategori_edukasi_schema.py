from pydantic import BaseModel

class KategoriEdukasiCreate(BaseModel):
    nama_kategori_edu: str


class KategoriEdukasiResponse(BaseModel):
    id_kategori_edu: int
    nama_kategori_edu: str

    class Config:
        from_attributes = True