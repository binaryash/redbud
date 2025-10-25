from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from content.models import Content, Training
from unittest.mock import patch, MagicMock
from datetime import date

User = get_user_model()


class TestContentViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            email="test@email.com",
            role="manager",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.training = Training.objects.create(
            name="Test Training",
            start_date=date.today(),
            end_date=date.today(),
            duration_days=1,
            created_by=self.user,
        )

        self.content = Content.objects.create(
            title="Test Content",
            training=self.training,
            content_type="text",
            text_content="This is a sample text content for testing.",
            created_by=self.user,
        )

    @patch("content.views.get_gemini_service")
    def test_summarize_text_content(self, mock_gemini_service):
        """Test summarizing text content"""
        # Mock the Gemini service
        mock_service_instance = MagicMock()
        mock_service_instance.summarize_text.return_value = "This is a summary."
        mock_gemini_service.return_value = mock_service_instance

        # Use reverse to get the correct URL (RECOMMENDED)
        url = reverse("content-summarize", kwargs={"pk": self.content.id})
        # This will give you: /api/content/contents/1/summarize/

        response = self.client.post(url, data={"max_length": 100}, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"], "This is a summary.")
        self.assertEqual(response.data["content_id"], self.content.id)
        self.assertEqual(response.data["content_type"], "text")
        self.assertEqual(response.data["max_length"], 100)

        # Verify mock was called correctly
        mock_service_instance.summarize_text.assert_called_once_with(
            self.content.text_content, 100
        )

    @patch("content.views.get_gemini_service")
    def test_summarize_pdf_content(self, mock_gemini_service):
        """Test summarizing PDF content"""
        # Create PDF content
        from django.core.files.uploadedfile import SimpleUploadedFile

        pdf_content = Content.objects.create(
            title="Test PDF",
            training=self.training,
            content_type="pdf",
            file=SimpleUploadedFile(
                "test.pdf", b"file_content", content_type="application/pdf"
            ),
            created_by=self.user,
        )

        # Mock the Gemini service
        mock_service_instance = MagicMock()
        mock_service_instance.summarize_pdf.return_value = "This is a PDF summary."
        mock_gemini_service.return_value = mock_service_instance

        url = reverse("content-summarize", kwargs={"pk": pdf_content.id})
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"], "This is a PDF summary.")

    @patch("content.views.get_gemini_service")
    def test_summarize_unsupported_content_type(self, mock_gemini_service):
        """Test summarizing unsupported content type (video, youtube, link)"""
        video_content = Content.objects.create(
            title="Test Video",
            training=self.training,
            content_type="video",
            created_by=self.user,
        )

        url = reverse("content-summarize", kwargs={"pk": video_content.id})
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("only supported for text and PDF", response.data["error"])

    @patch("content.views.get_gemini_service")
    def test_summarize_with_invalid_max_length(self, mock_gemini_service):
        """Test summarize with invalid max_length"""
        url = reverse("content-summarize", kwargs={"pk": self.content.id})

        # Test with too small max_length
        response = self.client.post(url, data={"max_length": 30}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with too large max_length
        response = self.client.post(url, data={"max_length": 1500}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with non-integer max_length
        response = self.client.post(url, data={"max_length": "invalid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
