from pydantic import BaseModel

class AgenPenyebabRespon(BaseModel):
    id_agen: int
    id_kategori: int
    nama_ilmiah: str
    jenis: str

    class Config:
        from_attributes = True
