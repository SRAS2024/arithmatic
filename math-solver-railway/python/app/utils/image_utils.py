"""Image utility functions for loading, converting, and encoding images."""

import base64
import io
from typing import Optional

try:
    from PIL import Image
except ImportError:
    Image = None


def load_image_from_bytes(data: bytes) -> "Image.Image":
    """Load a PIL Image from raw bytes.

    Args:
        data: Raw image bytes.

    Returns:
        PIL Image object.

    Raises:
        RuntimeError: If Pillow is not installed.
        ValueError: If the data cannot be decoded as an image.
    """
    if Image is None:
        raise RuntimeError("Pillow is not installed")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()  # force full load
        return img
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc


def image_to_bytes(img: "Image.Image", format: str = "PNG") -> bytes:
    """Convert a PIL Image to raw bytes in the given format.

    Args:
        img: PIL Image object.
        format: Output format (PNG, JPEG, etc.).

    Returns:
        Raw image bytes.
    """
    buf = io.BytesIO()
    save_kwargs = {}
    if format.upper() == "JPEG":
        # JPEG doesn't support alpha; convert if needed
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        save_kwargs["quality"] = 95
    img.save(buf, format=format, **save_kwargs)
    return buf.getvalue()


def image_to_base64(img: "Image.Image", format: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded string.

    Args:
        img: PIL Image object.
        format: Output format (PNG, JPEG, etc.).

    Returns:
        Base64-encoded string of the image.
    """
    raw = image_to_bytes(img, format=format)
    return base64.b64encode(raw).decode("utf-8")


def base64_to_image(b64_string: str) -> "Image.Image":
    """Decode a base64 string into a PIL Image.

    Args:
        b64_string: Base64-encoded image data (may include data-URI prefix).

    Returns:
        PIL Image object.
    """
    if Image is None:
        raise RuntimeError("Pillow is not installed")
    # Strip optional data-URI header
    if "," in b64_string and b64_string.startswith("data:"):
        b64_string = b64_string.split(",", 1)[1]
    raw = base64.b64decode(b64_string)
    return load_image_from_bytes(raw)
