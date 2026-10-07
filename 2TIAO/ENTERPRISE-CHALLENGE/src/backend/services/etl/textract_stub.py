"""AWS Textract stub — skeleton for future AWS integration.

Not yet implemented; credentials and configuration are loaded from env
for future use. Raises NotImplementedError when called.
"""

import logging
import os
from io import BytesIO

from services.etl.ocr_provider import OCRProvider

logger = logging.getLogger(__name__)


class TextractStub(OCRProvider):
    """Skeleton AWS Textract client for future integration.

    Parses AWS credentials and region from environment variables.
    Currently raises NotImplementedError; to enable, implement actual
    boto3 Textract calls and remove the NotImplementedError.

    Supported env vars:
    - TEXTRACT_REGION: AWS region (e.g., 'us-east-1')
    - AWS_ACCESS_KEY_ID: AWS access key
    - AWS_SECRET_ACCESS_KEY: AWS secret key
    """

    SUPPORTED_FORMATS = (".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    def __init__(self):
        """Initialize Textract client with AWS credentials from env."""
        self.region = os.getenv("TEXTRACT_REGION", "us-east-1")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")

        # Log configuration for debugging (without exposing secrets)
        logger.debug(
            "TextractStub initialized with region=%s, has_access_key=%s, has_secret_key=%s",
            self.region,
            bool(self.access_key),
            bool(self.secret_key),
        )

    def process_file(self, file_bytes: BytesIO) -> dict:
        """Process file with AWS Textract (stub).

        Not yet implemented. To enable:
        1. Uncomment the NotImplementedError below after removing this line
        2. Implement boto3 Textract integration
        3. Add boto3 to requirements.txt

        Args:
            file_bytes: Binary content of the file.

        Returns:
            NotImplementedError (currently).

        Raises:
            NotImplementedError: Textract integration not yet available.
        """
        raise NotImplementedError(
            "AWS Textract integration not yet implemented. "
            "Configuration is loaded from env vars (TEXTRACT_REGION, "
            "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) and ready for future use."
        )

    def supports_format(self, filename: str) -> bool:
        """Check if file format is supported by Textract.

        Args:
            filename: Filename or path.

        Returns:
            bool: True if extension matches supported formats.
        """
        filename_lower = filename.lower()
        return any(filename_lower.endswith(fmt) for fmt in self.SUPPORTED_FORMATS)
