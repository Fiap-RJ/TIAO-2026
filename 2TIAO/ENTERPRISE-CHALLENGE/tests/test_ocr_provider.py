"""Tests for OCR provider factory and implementations (hermetic, no real API calls)."""

import io
from unittest.mock import MagicMock, patch

import pytest

from services.etl.factory import get_ocr_provider
from services.etl.ocr_provider import OCRProvider
from services.etl.paddle_ocr_local import PaddleOCRLocal
from services.etl.textract_stub import TextractStub


class TestOCRProviderBase:
    """Test abstract OCR provider interface."""

    def test_provider_is_abstract(self):
        """OCRProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            OCRProvider()


class TestPaddleOCRLocal:
    """Tests for PaddleOCR HTTP client implementation."""

    @pytest.fixture
    def paddle_client(self):
        return PaddleOCRLocal()

    def test_supports_pdf(self, paddle_client):
        assert paddle_client.supports_format("document.pdf") is True
        assert paddle_client.supports_format("Document.PDF") is True

    def test_supports_images(self, paddle_client):
        assert paddle_client.supports_format("photo.jpg") is True
        assert paddle_client.supports_format("image.jpeg") is True
        assert paddle_client.supports_format("picture.png") is True
        assert paddle_client.supports_format("scan.bmp") is True
        assert paddle_client.supports_format("scan.tiff") is True
        assert paddle_client.supports_format("image.webp") is True

    def test_rejects_unsupported_formats(self, paddle_client):
        assert paddle_client.supports_format("document.txt") is False
        assert paddle_client.supports_format("data.xlsx") is False
        assert paddle_client.supports_format("video.mp4") is False

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_success(self, mock_post, paddle_client):
        """Test successful OCR processing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "lines": ["Line 1", "Line 2", "Line 3"],
        }
        mock_post.return_value = mock_response

        file_bytes = io.BytesIO(b"fake pdf content")
        result = paddle_client.process_file(file_bytes)

        assert result["lines"] == ["Line 1", "Line 2", "Line 3"]
        assert result["texts"] == "Line 1\nLine 2\nLine 3"
        mock_post.assert_called_once()

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_empty_result(self, mock_post, paddle_client):
        """Test OCR with empty result (no text extracted)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"lines": []}
        mock_post.return_value = mock_response

        file_bytes = io.BytesIO(b"blank page")
        result = paddle_client.process_file(file_bytes)

        assert result["lines"] == []
        assert result["texts"] == ""

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_connection_error(self, mock_post, paddle_client):
        """Test error when OCR service is unreachable."""
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        file_bytes = io.BytesIO(b"content")

        with pytest.raises(ValueError, match="service unavailable"):
            paddle_client.process_file(file_bytes)

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_timeout(self, mock_post, paddle_client):
        """Test timeout error from OCR service."""
        import requests

        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        file_bytes = io.BytesIO(b"content")

        with pytest.raises(ValueError, match="timeout"):
            paddle_client.process_file(file_bytes)

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_invalid_response(self, mock_post, paddle_client):
        """Test invalid/malformed response from OCR service."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid_key": "no_lines_here"}
        mock_post.return_value = mock_response

        file_bytes = io.BytesIO(b"content")
        result = paddle_client.process_file(file_bytes)

        # Should default to empty lines when 'lines' key is missing
        assert result["lines"] == []
        assert result["texts"] == ""

    @patch("services.etl.paddle_ocr_local.requests.post")
    def test_process_file_http_error(self, mock_post, paddle_client):
        """Test HTTP error from OCR service."""
        import requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_post.return_value = mock_response

        file_bytes = io.BytesIO(b"content")

        with pytest.raises(ValueError, match="service error"):
            paddle_client.process_file(file_bytes)


class TestTextractStub:
    """Tests for AWS Textract stub implementation."""

    @pytest.fixture
    def textract_client(self):
        return TextractStub()

    def test_supports_formats(self, textract_client):
        """Textract stub claims to support PDFs and images."""
        assert textract_client.supports_format("document.pdf") is True
        assert textract_client.supports_format("photo.jpg") is True
        assert textract_client.supports_format("photo.jpeg") is True
        assert textract_client.supports_format("image.png") is True
        assert textract_client.supports_format("scan.bmp") is True
        assert textract_client.supports_format("scan.tiff") is True

    def test_rejects_unsupported_formats(self, textract_client):
        assert textract_client.supports_format("document.txt") is False
        assert textract_client.supports_format("video.mp4") is False

    def test_process_file_not_implemented(self, textract_client):
        """Textract is a stub; calling process_file raises NotImplementedError."""
        file_bytes = io.BytesIO(b"content")

        with pytest.raises(NotImplementedError, match="not yet implemented"):
            textract_client.process_file(file_bytes)

    def test_loads_aws_credentials_from_env(self, monkeypatch):
        """TextractStub initializes with AWS credentials from env vars."""
        monkeypatch.setenv("TEXTRACT_REGION", "eu-west-1")
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-key")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret")

        client = TextractStub()

        assert client.region == "eu-west-1"
        assert client.access_key == "test-key"
        assert client.secret_key == "test-secret"

    def test_defaults_to_us_east_1(self, monkeypatch):
        """TextractStub defaults to us-east-1 if TEXTRACT_REGION not set."""
        monkeypatch.delenv("TEXTRACT_REGION", raising=False)
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

        client = TextractStub()

        assert client.region == "us-east-1"
        assert client.access_key == ""
        assert client.secret_key == ""


class TestOCRProviderFactory:
    """Tests for get_ocr_provider factory function."""

    def test_factory_returns_paddle_by_default(self, monkeypatch):
        """Factory returns PaddleOCRLocal when OCR_PROVIDER='paddle_local'."""
        from core.config import settings

        monkeypatch.setattr(settings, "OCR_PROVIDER", "paddle_local")

        provider = get_ocr_provider()

        assert isinstance(provider, PaddleOCRLocal)

    def test_factory_returns_textract_stub(self, monkeypatch):
        """Factory returns TextractStub when OCR_PROVIDER='textract'."""
        from core.config import settings

        monkeypatch.setattr(settings, "OCR_PROVIDER", "textract")

        provider = get_ocr_provider()

        assert isinstance(provider, TextractStub)

    def test_factory_rejects_unknown_provider(self, monkeypatch):
        """Factory raises ValueError for unknown provider."""
        from core.config import settings

        monkeypatch.setattr(settings, "OCR_PROVIDER", "unknown_provider")

        with pytest.raises(ValueError, match="Unknown OCR_PROVIDER"):
            get_ocr_provider()

    def test_factory_returns_subclass_of_ocr_provider(self, monkeypatch):
        """All factory implementations inherit from OCRProvider."""
        from core.config import settings

        monkeypatch.setattr(settings, "OCR_PROVIDER", "paddle_local")
        provider = get_ocr_provider()
        assert isinstance(provider, OCRProvider)

        monkeypatch.setattr(settings, "OCR_PROVIDER", "textract")
        provider = get_ocr_provider()
        assert isinstance(provider, OCRProvider)
