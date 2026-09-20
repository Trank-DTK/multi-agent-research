import tempfile
from pathlib import Path
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Dataset, AnalysisResult
from .views import DatasetDeleteView

class DatasetDeleteTests(TestCase):
    def test_delete_is_owner_scoped_and_removes_file_and_results(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            owner = get_user_model().objects.create_user(username='dataset-owner')
            other = get_user_model().objects.create_user(username='dataset-other')
            dataset = Dataset.objects.create(user=owner, name='test', file_name='test.csv', file=SimpleUploadedFile('test.csv', b'value\n1\n'))
            AnalysisResult.objects.create(dataset=dataset, analysis_type='descriptive')
            path = Path(dataset.file.path)
            request = APIRequestFactory().delete('/delete/')
            force_authenticate(request, user=other)
            self.assertEqual(DatasetDeleteView.as_view()(request,dataset_id=dataset.pk).status_code,404)
            self.assertTrue(path.exists())
            force_authenticate(request, user=owner)
            self.assertEqual(DatasetDeleteView.as_view()(request,dataset_id=dataset.pk).status_code,200)
            self.assertFalse(Dataset.objects.exists())
            self.assertFalse(AnalysisResult.objects.exists())
            self.assertFalse(path.exists())
