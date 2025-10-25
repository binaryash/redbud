from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from content.models import Content, Training
from unittest.mock import patch

User = get_user_model()

class TestContentViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', role='manager')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.training = Training.objects.create(name='Test Training')
        self.content = Content.objects.create(
            title='Test Content',
            training=self.training,
            content_type='text',
            text_content='This is a sample text content for testing.'
        )

    @patch('content.gemini_service.get_gemini_service')
    def test_summarize_text_content(self, mock_gemini_service):
        # Mock the Gemini service
        mock_service_instance = mock_gemini_service.return_value
        mock_service_instance.summarize_text.return_value = "This is a summary."

        url = f'/content/{self.content.id}/summarize/'
        response = self.client.post(url, data={'max_length': 100}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertEqual(response.data['summary'], "This is a summary.")
        self.assertEqual(response.data['content_id'], self.content.id)
        self.assertEqual(response.data['content_type'], 'text')
