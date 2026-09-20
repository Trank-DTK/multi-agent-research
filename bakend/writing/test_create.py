from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Paper, PaperSection
from .views import PaperCreateView

class PaperCreateTests(TestCase):
    def request(self):
        user = get_user_model().objects.create_user(username='creator')
        request = APIRequestFactory().post('/create/', {'title':'Draft','topic':'Research'}, format='json')
        force_authenticate(request,user=user)
        return request

    @patch('writing.views.WritingService')
    def test_outline_survives_reload(self, service):
        service.return_value.generate_outline.return_value = 'Methods\n<script>example</script>'
        response = PaperCreateView.as_view()(self.request())
        self.assertEqual(response.status_code,201)
        self.assertIn('Methods', Paper.objects.get().content)
        self.assertIn('&lt;script&gt;', PaperSection.objects.get().content)

    @patch('writing.views.WritingService')
    def test_failed_generation_does_not_leave_duplicate_draft(self, service):
        service.return_value.generate_outline.side_effect = ValueError('model unavailable')
        self.assertEqual(PaperCreateView.as_view()(self.request()).status_code,502)
        self.assertFalse(Paper.objects.exists())
