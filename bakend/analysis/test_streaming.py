from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Dataset
from .agent_views import AnalysisAgentChatView

class AnalysisStreamTests(TestCase):
    @patch('analysis.agent_views.DataAnalysisService.load_dataframe')
    @patch('analysis.agent_views.build_llm')
    def test_stream_contains_real_dataset_context(self, build, load):
        user = get_user_model().objects.create_user(username='analyst')
        dataset = Dataset.objects.create(user=user, name='Trial', file='test.csv', file_name='test.csv')
        import pandas as pd
        load.return_value = pd.DataFrame({'score':[1,2,3]})
        build.return_value.stream_chat.return_value = iter(['analysis', ' result'])
        request = APIRequestFactory().post('/agent/', {'message':'interpret', 'stream':True}, format='json')
        force_authenticate(request, user=user)
        response = AnalysisAgentChatView.as_view()(request, dataset_id=dataset.pk)
        self.assertTrue(response.streaming)
        self.assertIn(b'[DONE]', b''.join(response.streaming_content))
        self.assertIn('score', str(build.return_value.stream_chat.call_args))
        build.return_value.chat.assert_not_called()
