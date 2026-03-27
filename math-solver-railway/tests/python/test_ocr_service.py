"""
Arithmetic - OCR Service Tests
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from app.services.ocr_service import OCRService
from app.services.image_preprocess_service import ImagePreprocessService


class TestImagePreprocessing:
    """Tests for image preprocessing pipeline."""

    def test_grayscale_conversion(self):
        img = Image.new('RGB', (100, 100), color='white')
        result = ImagePreprocessService.to_grayscale(img)
        assert result.mode == 'L'

    def test_contrast_enhancement(self):
        img = Image.new('L', (100, 100), color=128)
        result = ImagePreprocessService.enhance_contrast(img)
        assert result is not None
        assert result.size == (100, 100)

    def test_denoise(self):
        img = Image.new('L', (100, 100), color=200)
        result = ImagePreprocessService.denoise(img)
        assert result is not None

    def test_threshold(self):
        img = Image.new('L', (100, 100), color=128)
        result = ImagePreprocessService.threshold(img)
        assert result is not None

    def test_resize_large_image(self):
        img = Image.new('RGB', (5000, 5000), color='white')
        result = ImagePreprocessService.resize_if_needed(img, max_dim=2000)
        assert max(result.size) <= 2000

    def test_small_image_not_resized(self):
        img = Image.new('RGB', (500, 500), color='white')
        result = ImagePreprocessService.resize_if_needed(img, max_dim=2000)
        assert result.size == (500, 500)


class TestOCRService:
    """Tests for OCR text extraction."""

    def test_process_blank_image(self):
        img = Image.new('RGB', (200, 50), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        result = OCRService.extract_text(buf.read())
        assert result is not None
        assert 'text' in result

    def test_confidence_reporting(self):
        img = Image.new('RGB', (200, 50), color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        result = OCRService.extract_text(buf.read())
        assert 'confidence' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
