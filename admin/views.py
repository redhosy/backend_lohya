import csv
import io
import os
import zipfile
from pathlib import Path

from fastapi import Request
from fastapi.responses import StreamingResponse, RedirectResponse
from sqladmin import Admin, ModelView, action
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from markupsafe import Markup

from app.core.config import get_settings
from app.db.database import engine, SessionLocal
from app.models.user_model import User
from app.models.kategori_klasifikasi_model import KategoriKlasifikasi
from app.models.agen_penyebab_model import AgenPenyebab
from app.models.edukasi_tani_model import EdukasiTani
from app.models.kategori_edukasi_model import KategoriEdukasi
from app.models.laporan_baru import LaporanBaru

settings = get_settings()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"admin_user": username})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_user") is not None


class CustomAdmin(Admin):
    async def index(self, request: Request):
        if not await self.authentication_backend.authenticate(request):
            return RedirectResponse(request.url_for("admin:login"))
        return RedirectResponse(request.url_for("admin:list", identity="user"))


class UserAdmin(ModelView, model=User):
    column_list = [User.id_user, User.email, User.nama, User.auth_provider, "total_scan", User.created_at]
    column_details_list = [User.id_user, User.email, User.nama, User.auth_provider, User.profile_image_url, User.is_verified, "total_scan", User.created_at, User.updated_at, User.last_login]
    column_searchable_list = [User.email, User.nama]
    column_sortable_list = [User.id_user, User.created_at]
    column_labels = {"total_scan": "Total Scan Daun"}
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
        User.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d") if m.updated_at else "",
        User.last_login: lambda m, a: m.last_login.strftime("%Y-%m-%d") if m.last_login else "",
    }
    can_create = False
    can_edit = False
    can_delete = False
    can_export = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"


class KategoriAdmin(ModelView, model=KategoriKlasifikasi):
    column_list = [
        KategoriKlasifikasi.id_kategori,
        KategoriKlasifikasi.kode_kelas,
        KategoriKlasifikasi.kategori,
    ]
    column_details_list = [
        KategoriKlasifikasi.id_kategori,
        KategoriKlasifikasi.kode_kelas,
        KategoriKlasifikasi.kategori,
        "agen_penyebab_list",
        KategoriKlasifikasi.deskripsi,
        KategoriKlasifikasi.perawatan,
        KategoriKlasifikasi.pencegahan,
        KategoriKlasifikasi.referensi,
        KategoriKlasifikasi.is_default,
    ]
    column_labels = {
        KategoriKlasifikasi.referensi: "Referensi (JSON)",
        "agen_penyebab_list": "Agen Penyebab",
    }
    column_formatters_detail = {
        "agen_penyebab_list": lambda m, a: Markup(
            "<br>".join(
                f'<span class="badge bg-white">{ag.nama_ilmiah} ({ag.jenis})</span>'
                for ag in m.agen_penyebab_rel
            )
        ) if m.agen_penyebab_rel else "<em>Tidak ada agen penyebab</em>",
        KategoriKlasifikasi.referensi: lambda m, a: Markup(
            f'<div>{m.referensi}</div>'
        ) if m.referensi else Markup('<small class="text-muted">Format: [{\"judul\": \"Judul Referensi\", \"sumber\": \"Sumber\", \"url\": \"https://link.com\"}]</small>'),
    }
    form_args = {
        "agen_penyebab_rel": {
            "label": "Agen Penyebab",
        },
        "referensi": {
            "description": "Masukkan referensi dalam format JSON array. Contoh: [{\"judul\": \"Judul Referensi\", \"sumber\": \"Sumber\", \"url\": \"https://link.com\"}]",
        },
        "pencegahan":{
            "description": "Masukkan langkah pencegahan dalam format JSON array. Contoh: [\"Langkah 1\", \"Langkah 2\"]",
        },
        "perawatan":{
            "description": "Masukkan langkah perawatan dalam format JSON array. Contoh: [\"Langkah 1\", \"Langkah 2\"]",
        }
    }
    column_sortable_list = [KategoriKlasifikasi.id_kategori]
    form_columns = [
        KategoriKlasifikasi.kode_kelas,
        KategoriKlasifikasi.kategori,
        KategoriKlasifikasi.agen_penyebab_rel,
        KategoriKlasifikasi.deskripsi,
        KategoriKlasifikasi.perawatan,
        KategoriKlasifikasi.pencegahan,
        KategoriKlasifikasi.referensi,
        KategoriKlasifikasi.is_default,
    ]
    can_create = False
    can_delete = False
    can_export = False
    name = "Kategori"
    name_plural = "Kategori Klasifikasi"
    icon = "fa-solid fa-tags"
    edit_template = "admin/kategori_edit.html"


class AgenPenyebabAdmin(ModelView, model=AgenPenyebab):
    column_list = [
        AgenPenyebab.id_agen,
        AgenPenyebab.id_kategori,
        AgenPenyebab.nama_ilmiah,
        AgenPenyebab.jenis,
    ]
    column_details_list = [
        AgenPenyebab.id_agen,
        AgenPenyebab.id_kategori,
        AgenPenyebab.nama_ilmiah,
        AgenPenyebab.jenis,
    ]
    column_labels = {
        AgenPenyebab.id_kategori: "Kategori Klasifikasi",
        AgenPenyebab.nama_ilmiah: "Nama Ilmiah",
        AgenPenyebab.jenis: "Jenis",
    }
    column_searchable_list = [AgenPenyebab.nama_ilmiah, AgenPenyebab.jenis]
    column_sortable_list = [AgenPenyebab.id_agen]
    form_columns = [
        AgenPenyebab.id_kategori,
        AgenPenyebab.nama_ilmiah,
        AgenPenyebab.jenis,
    ]
    form_args = {
        "id_kategori": {"label": "Kategori Klasifikasi"},
        "nama_ilmiah": {"label": "Nama Ilmiah"},
        "jenis": {"label": "Jenis"},
    }
    can_create = False
    can_delete = False
    can_export = False
    name = "Agen Penyebab"
    name_plural = "Agen Penyebab"
    icon = "fa-solid fa-bug"


class KategoriEdukasiAdmin(ModelView, model=KategoriEdukasi):
    column_list = [KategoriEdukasi.id_kategori_edu, KategoriEdukasi.nama_kategori_edu]
    form_columns = [KategoriEdukasi.nama_kategori_edu]
    column_details_list = [KategoriEdukasi.id_kategori_edu, KategoriEdukasi.nama_kategori_edu]
    column_searchable_list = [KategoriEdukasi.nama_kategori_edu]
    can_export = False
    name = "Kategori Edukasi"
    name_plural = "Kategori Edukasi"
    icon = "fa-solid fa-folder"


class EdukasiAdmin(ModelView, model=EdukasiTani):
    column_list = [
        EdukasiTani.id_edukasi,
        EdukasiTani.judul,
        "kategori_edu_name",
        "kategori_klasifikasi_name",
        EdukasiTani.created_at,
    ]
    column_details_list = [
        EdukasiTani.id_edukasi,
        EdukasiTani.judul,
        "kategori_edu_name",
        "kategori_klasifikasi_name",
        EdukasiTani.gambar,
        EdukasiTani.ringkasan,
        EdukasiTani.content,
        EdukasiTani.referensi,
        EdukasiTani.created_at,
    ]
    column_labels = {
        "kategori_edu_name": "Kategori Edukasi",
        "kategori_klasifikasi_name": "Kategori Klasifikasi",
        EdukasiTani.id_kategori_edu: "Kategori Edukasi",
        EdukasiTani.id_kategori_klasifikasi: "Kategori Klasifikasi",
        EdukasiTani.referensi: "Referensi (JSON)",
    }
    column_searchable_list = [EdukasiTani.judul]
    column_sortable_list = [EdukasiTani.id_edukasi, EdukasiTani.created_at]
    column_formatters = {
        EdukasiTani.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
        "kategori_edu_name": lambda m, a: m.kategori_edu_rel.nama_kategori_edu if m.kategori_edu_rel else "-",
        "kategori_klasifikasi_name": lambda m, a: m.kategori_klasifikasi_rel.kategori if m.kategori_klasifikasi_rel else "-",
    }
    column_formatters_detail = {
        EdukasiTani.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
        "kategori_edu_name": lambda m, a: m.kategori_edu_rel.nama_kategori_edu if m.kategori_edu_rel else "-",
        "kategori_klasifikasi_name": lambda m, a: m.kategori_klasifikasi_rel.kategori if m.kategori_klasifikasi_rel else "-",
        EdukasiTani.referensi: lambda m, a: Markup(
            f'<div>{m.referensi}</div>'
        ) if m.referensi else Markup('<small class="text-muted">Format: [{\"judul\": \"Judul Referensi\", \"instansi\": \"Instansi\", \"url\": \"https://link.com\", \"tahun\": \"Tahun\", \"catatan\": \"Catatan\"}]</small>'),
    }
    form_columns = [
        EdukasiTani.judul,
        EdukasiTani.kategori_edu_rel,
        EdukasiTani.kategori_klasifikasi_rel,
        EdukasiTani.gambar,
        EdukasiTani.ringkasan,
        EdukasiTani.content,
        EdukasiTani.referensi,
    ]
    form_args = {
        "referensi": {
            "description": "Masukkan referensi dalam format JSON array. Contoh: [{\"judul\": \"Judul Referensi\", \"instansi\": \"Instansi\", \"url\": \"https://link.com\", \"tahun\": \"Tahun\", \"catatan\": \"Catatan\"}]",
        },
        "kategori_edu_rel": {
            "label": "Kategori Edukasi",
        },
        "kategori_klasifikasi_rel": {
            "label": "Kategori Klasifikasi",
        },
    }
    can_export = False
    name = "Edukasi"
    name_plural = "Edukasi Tani"
    icon = "fa-solid fa-book"


class LaporanAdmin(ModelView, model=LaporanBaru):
    column_list = [
        LaporanBaru.id,
        LaporanBaru.user_id,
        LaporanBaru.foto_url,
        LaporanBaru.deskripsi_masalah,
        LaporanBaru.status,
        LaporanBaru.created_at,
    ]
    column_details_list = [
        LaporanBaru.id,
        LaporanBaru.user_id,
        LaporanBaru.foto_url,
        LaporanBaru.deskripsi_masalah,
        LaporanBaru.status,
        LaporanBaru.created_at,
    ]
    column_labels = {LaporanBaru.foto_url: "Foto"}
    column_searchable_list = [LaporanBaru.deskripsi_masalah]
    column_sortable_list = [LaporanBaru.id, LaporanBaru.created_at, LaporanBaru.status]
    column_formatters = {
        LaporanBaru.foto_url: lambda m, a: Markup(f'<img src="{m.foto_url}" style="max-height:80px;border-radius:4px;" />') if m.foto_url else "",
        LaporanBaru.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
        LaporanBaru.status: lambda m, a: (
            Markup(
                f'<a href="/admin/laporan-baru/edit/{m.id}" '
                f'style="display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-decoration:none;color:#fff;'
                f'background-color:#2fb344;cursor:pointer;" '
                f'title="Klik untuk ubah status">'
                f'dibaca</a>'
            ) if m.status == "dibaca"
            else Markup(
                f'<a href="/admin/laporan-baru/edit/{m.id}" '
                f'style="display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-decoration:none;color:#fff;'
                f'background-color:#f59f00;cursor:pointer;" '
                f'title="Klik untuk ubah status">'
                f'pending</a>'
            )
        ),
    }
    column_formatters_detail = {
        LaporanBaru.foto_url: lambda m, a: Markup(f'<img src="{m.foto_url}" style="max-height:200px;border-radius:8px;margin:10px 0;" />') if m.foto_url else "Tidak ada foto",
        LaporanBaru.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
    }
    can_create = False
    can_edit = True
    can_delete = True
    can_export = False
    name = "Laporan"
    name_plural = "Laporan Baru"
    icon = "fa-solid fa-flag"

    @action(
        name="export_zip",
        label="Export ZIP",
        confirmation_message="Export semua data laporan ke ZIP (CSV + Gambar)?",
    )
    async def export_zip(self, request: Request):
        db = SessionLocal()
        try:
            result = db.execute(select(LaporanBaru).order_by(LaporanBaru.id))
            laporans = result.scalars().all()
        finally:
            db.close()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["id", "user_id", "deskripsi_masalah", "status", "created_at", "foto_filename"])

            for lp in laporans:
                foto_filename = ""
                if lp.foto_url:
                    foto_filename = Path(lp.foto_url).name
                    full_path = os.path.join(settings.UPLOAD_DIR, "laporan", foto_filename)
                    if os.path.exists(full_path):
                        zf.write(full_path, f"images/{foto_filename}")

                writer.writerow([
                    lp.id, lp.user_id, lp.deskripsi_masalah, lp.status,
                    lp.created_at.isoformat() if lp.created_at else "", foto_filename,
                ])

            zf.writestr("metadata_laporan.csv", csv_output.getvalue())

        zip_buffer.seek(0)
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=laporan_baru.zip"},
        )


def setup_admin(app):
    admin = CustomAdmin(
        app=app,
        engine=engine,
        authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
    )

    admin.add_view(UserAdmin)
    admin.add_view(KategoriAdmin)
    admin.add_view(AgenPenyebabAdmin)
    admin.add_view(KategoriEdukasiAdmin)
    admin.add_view(EdukasiAdmin)
    admin.add_view(LaporanAdmin)

    return admin
