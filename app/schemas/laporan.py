from pydantic import BaseModel
from datetime import datetime


class LaporanCreate(BaseModel):
    deskripsi_masalah: str


class LaporanResponse(BaseModel):
    id: int
    user_id: int
    foto_url: str
    deskripsi_masalah: str
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
