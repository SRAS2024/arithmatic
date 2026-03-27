import os
import uuid
import tempfile
import shutil
from pathlib import Path
from app.config import settings


def get_temp_dir() -> str:
    """Get the temporary directory, creating it if needed."""
    path = Path(settings.TEMP_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def create_temp_file(suffix: str = "", prefix: str = "arith_") -> str:
    """Create a temporary file and return its path."""
    temp_dir = get_temp_dir()
    filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
    filepath = os.path.join(temp_dir, filename)
    Path(filepath).touch()
    return filepath


def save_upload_to_temp(content: bytes, suffix: str = "") -> str:
    """Save uploaded file content to a temporary file."""
    filepath = create_temp_file(suffix=suffix)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath


def cleanup_temp_file(filepath: str) -> None:
    """Remove a temporary file if it exists."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass


def cleanup_temp_dir(dirpath: str) -> None:
    """Remove a temporary directory and its contents."""
    try:
        if dirpath and os.path.exists(dirpath):
            shutil.rmtree(dirpath)
    except OSError:
        pass


def cleanup_old_temp_files(max_age_seconds: int = 3600) -> int:
    """Remove temporary files older than max_age_seconds. Returns count removed."""
    import time

    temp_dir = get_temp_dir()
    removed = 0
    now = time.time()
    try:
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                age = now - os.path.getmtime(filepath)
                if age > max_age_seconds:
                    os.remove(filepath)
                    removed += 1
    except OSError:
        pass
    return removed


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return Path(filename).suffix.lower()


def is_image_file(filename: str) -> bool:
    """Check if filename has an image extension."""
    return get_file_extension(filename) in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}


def is_pdf_file(filename: str) -> bool:
    """Check if filename has a PDF extension."""
    return get_file_extension(filename) == ".pdf"
