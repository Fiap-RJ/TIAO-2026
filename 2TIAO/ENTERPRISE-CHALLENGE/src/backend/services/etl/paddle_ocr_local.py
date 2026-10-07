


"""PaddleOCR local HTTP client — calls localhost:8100 /ocr endpoint."""

import logging
from io import BytesIO

import requests

from services.etl.ocr_provider import OCRProvider

logger = logging.getLogger(__name__)


class PaddleOCRLocal(OCRProvider):
    """HTTP client for local PaddleOCR service running on port 8100.

    Sends requests to localhost:8100/ocr and expects JSON response with
    extracted text lines. Supports PDFs and common image formats.
    """

    SUPPORTED_FORMATS = (".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")
    PADDLE_SERVICE_URL = "http://localhost:8100/ocr"
    REQUEST_TIMEOUT = 30  # seconds

    def process_file(self, file_bytes: BytesIO) -> dict:
        """Send file to PaddleOCR service and extract text.

        Args:
            file_bytes: Binary content of the file.

        Returns:
            dict with 'lines' (List[str]) and 'texts' (str) keys.

        Raises:
            ValueError: If service is unreachable, request fails, or processing fails.
        """
        try:
            file_bytes.seek(0)  # Ensure we read from the start
            files = {"file": ("document", file_bytes, "application/octet-stream")}

            response = requests.post(
                self.PADDLE_SERVICE_URL,
                files=files,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            result = response.json()

            # Expect result to contain 'lines' (list) key from PaddleOCR service
            lines = result.get("lines", [])
            texts = "\n".join(lines) if lines else ""

            logger.info(
                "PaddleOCR processed file successfully; extracted %d lines", len(lines)
            )

            return {"lines": lines, "texts": texts}

        except requests.exceptions.ConnectionError as e:
            logger.error("PaddleOCR service unreachable at %s", self.PADDLE_SERVICE_URL)
            raise ValueError(
                f"OCR service unavailable at {self.PADDLE_SERVICE_URL}: {str(e)}"
            ) from e
        except requests.exceptions.Timeout as e:
            logger.error("PaddleOCR service request timed out")
            raise ValueError(f"OCR service timeout after {self.REQUEST_TIMEOUT}s: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            logger.error("PaddleOCR request failed: %s", str(e))
            raise ValueError(f"OCR service error: {str(e)}") from e
        except (KeyError, ValueError) as e:
            logger.error("Failed to parse PaddleOCR response: %s", str(e))
            raise ValueError(f"Invalid OCR service response: {str(e)}") from e

    def supports_format(self, filename: str) -> bool:
        """Check if file format is supported by PaddleOCR.

        Args:
            filename: Filename or path.

        Returns:
            bool: True if extension matches supported formats.
        """
        filename_lower = filename.lower()
        return any(filename_lower.endswith(fmt) for fmt in self.SUPPORTED_FORMATS)
