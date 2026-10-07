"""Factory function for creating OCR provider instances."""

import logging
from typing import Literal

from core.config import settings
from services.etl.ocr_provider import OCRProvider
from services.etl.paddle_ocr_local import PaddleOCRLocal
from services.etl.textract_stub import TextractStub

logger = logging.getLogger(__name__)

OCRProviderType = Literal["paddle_local", "textract"]


def get_ocr_provider() -> OCRProvider:
    """Factory function to get OCR provider instance based on configuration.

    Reads OCR_PROVIDER env var (defaults to 'paddle_local').

    Returns:
        OCRProvider: Instance of the configured OCR provider.

    Raises:
        ValueError: If OCR_PROVIDER is not recognized.
    """
    provider_name: OCRProviderType = settings.OCR_PROVIDER  # type: ignore

    if provider_name == "paddle_local":
        logger.debug("Using PaddleOCR local HTTP client (localhost:8100)")
        return PaddleOCRLocal()
    elif provider_name == "textract":
        logger.debug("Using AWS Textract (stub)")
        return TextractStub()
    else:
        raise ValueError(
            f"Unknown OCR_PROVIDER '{provider_name}'. "
            f"Supported: 'paddle_local', 'textract'"
        )
