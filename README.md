# Pantau Cabai - Backend API

Backend API untuk aplikasi Pantau Cabai - klasifikasi penyakit daun cabai.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 14
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Admin Panel**: SQLAdmin
- **Auth**: JWT + Google OAuth

## Fitur

- Autentikasi user (register, login, OTP, Google OAuth)
- Klasifikasi penyakit daun cabai (simpan hasil)
- Riwayat klasifikasi
- Edukasi pertanian
- Kategori klasifikasi & agen penyebab
- Laporan user
- Koleksi user
- Admin panel
- Upload gambar dengan thumbnail

## Deploy dengan Docker

### Prerequisites

- Docker
- Docker Compose

### Langkah Deploy

1. **Clone repository**

```bash
git clone <repo-url>
cd backend
```

2. **Buat file `.env`**

```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

3. **Jalankan dengan Docker Compose**

```bash
docker-compose up -d --build
```

4. **Cek status**

```bash
docker-compose ps
docker-compose logs -f api
```

5. **Akses**

- API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs

### Perintah Docker

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Lihat logs
docker-compose logs -f api

# Masuk ke container
docker exec -it pantau_cabai_api sh

# Backup database
docker exec pantau_cabai_db pg_dump -U postgres pantau_cabai > backup.sql

# Restore database
cat backup.sql | docker exec -i pantau_cabai_db psql -U postgres pantau_cabai
```

## Development Lokal

### Prerequisites

- Python 3.13+
- PostgreSQL

### Setup

1. **Buat virtual environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup database**

```bash
# Buat database PostgreSQL
createdb pantau_cabai

# Jalankan migration
alembic upgrade head
```

4. **Jalankan server**

```bash
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:12345678@localhost:5432/pantau_cabai` |
| `SECRET_KEY` | JWT secret key | - |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `60` |
| `ADMIN_USERNAME` | Admin panel username | `admin` |
| `ADMIN_PASSWORD` | Admin panel password | `admin123` |
| `MAIL_USERNAME` | Email SMTP username | - |
| `MAIL_PASSWORD` | Email SMTP password | - |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `UPLOAD_DIR` | Upload directory | `uploads` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `5242880` |

## API Endpoints

### Auth
- `POST /api/register` - Register user
- `POST /api/login` - Login
- `POST /api/verify-otp` - Verifikasi OTP
- `POST /api/google-login` - Login dengan Google

### Klasifikasi
- `POST /api/simpan-hasil` - Simpan hasil klasifikasi
- `GET /api/riwayat-klasifikasi` - Ambil riwayat
- `GET /api/riwayat-klasifikasi/{id}` - Ambil riwayat by ID
- `DELETE /api/riwayat-klasifikasi/{id}` - Hapus riwayat

### Edukasi
- `GET /api/edukasi` - List edukasi
- `GET /api/edukasi/{id}` - Detail edukasi

### Kategori
- `GET /api/kategori` - List kategori klasifikasi

### Profil
- `GET /api/profile/{id}` - Ambil profil
- `PUT /api/profile/{id}` - Update profil

### Koleksi
- `GET /api/koleksi` - List koleksi user
- `POST /api/koleksi` - Tambah ke koleksi
- `DELETE /api/koleksi/{id}` - Hapus dari koleksi

### Laporan
- `POST /api/laporan` - Buat laporan
- `GET /api/laporan` - List laporan

## struktur Project

```
backend/
├── admin/              # Admin panel views
├── alembic/            # Database migrations
├── app/
│   ├── api/            # API routes
│   ├── auth/           # Auth logic (JWT, OTP, Google)
│   ├── core/           # Config, logging
│   ├── data/           # Static data (JSON)
│   ├── db/             # Database setup, seed
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── services/       # Business logic
├── templates/          # Custom admin templates
├── uploads/            # Uploaded files
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── requirements.txt
```
