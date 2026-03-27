"""Image preprocessing pipeline for OCR."""

import logging

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


class ImagePreprocessService:
    """Collection of static image-preprocessing methods using Pillow."""

    @staticmethod
    def to_grayscale(img: "Image.Image") -> "Image.Image":
        """Convert image to grayscale (mode 'L')."""
        if img.mode != "L":
            return img.convert("L")
        return img.copy()

    @staticmethod
    def enhance_contrast(img: "Image.Image", factor: float = 2.0) -> "Image.Image":
        """Enhance image contrast by the given factor.

        Args:
            img: PIL Image.
            factor: 1.0 = no change, >1 increases contrast.
        """
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    @staticmethod
    def denoise(img: "Image.Image") -> "Image.Image":
        """Apply a median filter to reduce noise."""
        return img.filter(ImageFilter.MedianFilter(size=3))

    @staticmethod
    def threshold(img: "Image.Image", thresh: int = 128) -> "Image.Image":
        """Binarise an image using a simple threshold.

        Pixels >= thresh become white (255), others become black (0).
        """
        gray = ImagePreprocessService.to_grayscale(img)
        return gray.point(lambda p: 255 if p >= thresh else 0, mode="L")

    @staticmethod
    def resize_if_needed(img: "Image.Image", max_dim: int = 2000) -> "Image.Image":
        """Down-scale the image so that neither dimension exceeds *max_dim*.

        The aspect ratio is preserved.  If the image is already smaller
        than *max_dim* on both axes it is returned unchanged.
        """
        w, h = img.size
        if w <= max_dim and h <= max_dim:
            return img
        scale = min(max_dim / w, max_dim / h)
        new_size = (int(w * scale), int(h * scale))
        return img.resize(new_size, Image.LANCZOS)

    @staticmethod
    def deskew(img: "Image.Image") -> "Image.Image":
        """Attempt to straighten a slightly rotated image.

        Uses a simple projection-profile approach on a binarised copy.
        Falls back to the original if the rotation angle is negligible.
        """
        try:
            import numpy as np

            gray = ImagePreprocessService.to_grayscale(img)
            bw = ImagePreprocessService.threshold(gray, 128)
            arr = np.array(bw)

            # Invert so text is white-on-black for projection
            arr = 255 - arr

            best_angle = 0.0
            best_score = 0.0
            for angle_10x in range(-50, 51, 5):  # -5.0 to +5.0 degrees
                angle = angle_10x / 10.0
                rotated = bw.rotate(angle, fillcolor=255)
                rot_arr = 255 - np.array(rotated)
                row_sums = rot_arr.sum(axis=1).astype(float)
                score = float(np.var(row_sums))
                if score > best_score:
                    best_score = score
                    best_angle = angle

            if abs(best_angle) < 0.3:
                return img
            return img.rotate(best_angle, expand=True, fillcolor=255)
        except ImportError:
            # numpy not available; skip deskew
            return img
        except Exception:
            return img

    @staticmethod
    def preprocess_for_ocr(img: "Image.Image") -> "Image.Image":
        """Full preprocessing pipeline suitable for OCR.

        Steps: resize -> grayscale -> denoise -> contrast -> threshold -> deskew.
        """
        img = ImagePreprocessService.resize_if_needed(img)
        img = ImagePreprocessService.to_grayscale(img)
        img = ImagePreprocessService.denoise(img)
        img = ImagePreprocessService.enhance_contrast(img, factor=1.8)
        img = ImagePreprocessService.threshold(img, thresh=140)
        img = ImagePreprocessService.deskew(img)
        return img
