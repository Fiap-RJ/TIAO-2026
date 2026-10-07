"""Abstract OCR provider interface — parametrized document processing."""

from abc import ABC, abstractmethod
from io import BytesIO


class OCRProvider(ABC):
    """Abstract base class for OCR providers.

    Implementations must support PDF and image formats.
    All processing is in-memory; no disk writes for production.
    """

    @abstractmethod
    def process_file(self, file_bytes: BytesIO) -> dict:
        """Process a document file (PDF or image) and extract text.

        Args:
            file_bytes: Binary content of the file as a BytesIO object.

        Returns:
            dict with keys:
            - 'lines': List of extracted text lines (List[str])
            - 'texts': Combined text as a single string

        Raises:
            ValueError: If file format is not supported or processing fails.
        """
        pass

    @abstractmethod
    def supports_format(self, filename: str) -> bool:
        """Check if the provider supports the file format.

        Args:
            filename: Filename or path to check.

        Returns:
            bool: True if format is supported, False otherwise.
        """
        pass
