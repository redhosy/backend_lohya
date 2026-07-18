from sqlalchemy import text
from app.db.database import engine, Base
from app.models.user_model import User
from app.models.otp_verification_model import OtpVerification
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.agen_penyebab_model import AgenPenyebab
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi
from app.models.edukasi_tani_model import EdukasiTani
from app.models.kategori_edukasi_model import KategoriEdukasi
from app.models.koleksi_user_model import KoleksiUser

print("Dropping all tables with CASCADE...")
with engine.begin() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Done! Tables reset.")
