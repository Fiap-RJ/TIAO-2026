"""ETL module — parametrized document processing with abstract OCR provider interface."""

from services.etl.factory import get_ocr_provider
from services.etl.ocr_provider import OCRProvider

__all__ = ["OCRProvider", "get_ocr_provider"]
