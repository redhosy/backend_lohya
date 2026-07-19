from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/nama_database"
    SECRET_KEY: str = "change-me-to-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    GOOGLE_CLIENT_ID: str = ""

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Loaded config - ADMIN_USERNAME: {self.ADMIN_USERNAME}, ADMIN_PASSWORD: {self.ADMIN_PASSWORD}")

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    THUMBNAIL_SIZE: str = "(300,300)"

    @property
    def thumbnail_size_tuple(self) -> tuple[int, int]:
        try:
            s = self.THUMBNAIL_SIZE.strip("()")
            w, h = s.split(",")
            return (int(w.strip()), int(h.strip()))
        except (ValueError, AttributeError):
            return (300, 300)

    class Config:
        env_file = ".env"


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    return settings
