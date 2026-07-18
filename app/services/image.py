import asyncio
import os
import uuid
from pathlib import Path

import aiofiles
from PIL import Image

from app.core.config import get_settings

settings = get_settings()


def _create_thumbnail_sync(image_path: str, thumbnail_path: str, size: tuple[int, int]) -> None:
    with Image.open(image_path) as img:
        img.thumbnail(size, Image.LANCZOS)
        img.save(thumbnail_path, quality=85, optimize=True)


async def save_image_and_create_thumbnail(
    file_content: bytes,
    original_filename: str,
    subfolder: str = "general",
) -> tuple[str, str]:
    ext = Path(original_filename).suffix.lower() or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    thumbnail_dir = os.path.join(upload_dir, "thumbnails")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(thumbnail_dir, exist_ok=True)

    image_path = os.path.join(upload_dir, unique_name)
    thumbnail_path = os.path.join(thumbnail_dir, f"thumb_{unique_name}")

    async with aiofiles.open(image_path, "wb") as f:
        await f.write(file_content)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _create_thumbnail_sync,
        image_path,
        thumbnail_path,
        settings.thumbnail_size_tuple,
    )

    image_url = f"/uploads/{subfolder}/{unique_name}"
    thumbnail_url = f"/uploads/{subfolder}/thumbnails/thumb_{unique_name}"

    return image_url, thumbnail_url
