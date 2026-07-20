from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  

from app.api.routes import router as root_router
from app.api.auth_router import router as auth_router
from app.api.simpan_hasil_router import router as simpan_hasil_router
from app.api.edukasi_router import router as edukasi_router
from app.api.kategori_router import router as kategori_router
from app.api.charts_router import router as charts_router
from app.api.profile_router import router as profile_router
from app.api.koleksi_router import router as koleksi_router
from app.api.laporan import router as laporan_router
from app.core.logging import logger
from app.db.database import engine, Base
from app.models.user_model import User
from app.models.otp_verification_model import OtpVerification
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.agen_penyebab_model import AgenPenyebab
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi
from app.models.edukasi_tani_model import EdukasiTani
from app.models.kategori_edukasi_model import KategoriEdukasi
from app.models.koleksi_user_model import KoleksiUser
from app.models.laporan_baru import LaporanBaru
from admin.views import setup_admin


logger.info("Database tables created/verified")


app = FastAPI(
    title="Pantau Cabai API",
    description="Backend API untuk klasifikasi visual daun cabai",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pantaucabai.redoksy.cloud"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(simpan_hasil_router, prefix="/api")
app.include_router(edukasi_router, prefix="/api")
app.include_router(kategori_router, prefix="/api")
app.include_router(charts_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(koleksi_router, prefix="/api")
app.include_router(laporan_router, prefix="/api")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

setup_admin(app)

logger.info("Pantau Cabai API started")
