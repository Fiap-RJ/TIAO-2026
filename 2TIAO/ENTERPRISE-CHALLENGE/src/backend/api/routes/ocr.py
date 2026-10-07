"""OCR endpoint — parametrized document processing with bearer token authentication."""

import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, File, Header, HTTPException, UploadFile, status

from core.config import settings
from domain.schemas import OCRResponse
from services.etl import get_ocr_provider

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_token(authorization: str | None) -> None:
    """Verify bearer token from Authorization header.

    Args:
        authorization: Authorization header value (e.g., 'Bearer token123').

    Raises:
        HTTPException: If token is missing or invalid (401).
    """
    if not settings.OCR_TOKEN:
        logger.warning("OCR_TOKEN not configured; all requests will be rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OCR service not configured (OCR_TOKEN empty)",
        )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format (expected 'Bearer <token>')",
        )

    if token != settings.OCR_TOKEN:
        logger.warning("Invalid OCR token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post("/", response_model=OCRResponse)
async def process_document(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
) -> OCRResponse:
    """Process a document (PDF or image) and extract text via OCR.

    Requires valid Bearer token in Authorization header (from OCR_TOKEN env var).
    Supports PDF and common image formats (JPEG, PNG, BMP, TIFF, WebP).
    All processing is in-memory; no disk writes.

    Args:
        file: Document file to process.
        authorization: Bearer token header (checked via _verify_token).

    Returns:
        OCRResponse with request_id, extracted lines, and combined text.

    Raises:
        401: If token is missing or invalid.
        422: If file format is not supported.
        500: If OCR processing fails.
    """
    _verify_token(authorization)

    req_id = str(uuid.uuid4())
    logger.info("OCR request received (request_id=%s, filename=%s)", req_id, file.filename)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename required",
        )

    try:
        provider = get_ocr_provider()

        # Check if format is supported
        if not provider.supports_format(file.filename):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported file format: {file.filename}. "
                f"Supported: PDF, JPEG, PNG, BMP, TIFF, WebP",
            )

        # Read file content into memory
        file_content = await file.read()
        file_bytes = BytesIO(file_content)

        # Process file
        result = provider.process_file(file_bytes)

        logger.info(
            "OCR processing successful (request_id=%s, lines=%d)",
            req_id,
            len(result.get("lines", [])),
        )

        return OCRResponse(
            request_id=req_id,
            lines=result.get("lines", []),
            texts=result.get("texts", ""),
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error("OCR processing error (request_id=%s): %s", req_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during OCR processing (request_id=%s)", req_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during OCR processing (request_id={req_id})",
        ) from e
