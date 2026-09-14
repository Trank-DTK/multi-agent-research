import tempfile
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from .models import Document, DocumentChunk
from .context import research_context

class UploadTests(TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.settings=override_settings(MEDIA_ROOT=self.tmp.name)
        self.settings.enable()
        self.addCleanup(self.settings.disable)
        self.user=get_user_model().objects.create_user(username='owner')
        self.client=APIClient()
        self.client.force_authenticate(self.user)
    def upload(self):
        return self.client.post('/documents/upload/',{'file':SimpleUploadedFile('research.pdf',b'%PDF-1.4 test fixture',content_type='application/pdf')},format='multipart')
    @patch('documents.views.PDFParseService.extract_text_from_pdf',return_value=('中文研究证据。实验方法及结果。',1))
    def test_upload_without_model_service(self, parse):
        with patch('documents.services.VectorService.generate_embedding',side_effect=AssertionError('must not call model')):
            response=self.upload()
        self.assertEqual(response.status_code,201,response.content)
        doc=Document.objects.get()
        self.assertTrue(doc.chunks.exists())
        self.assertIsNone(doc.chunks.first().embedding)
        self.assertTrue(Path(doc.file.path).exists())
        self.assertIn('研究证据',research_context(self.user,'研究证据',[doc.id]))
    @patch('documents.views.PDFParseService.extract_text_from_pdf',return_value=('',1))
    def test_scanned_pdf_rejected_and_file_removed(self, parse):
        self.assertEqual(self.upload().status_code,400)
        self.assertFalse(Document.objects.exists())
        self.assertEqual(list(Path(self.tmp.name).rglob('*.pdf')),[])
    @patch('documents.views.PDFParseService.extract_text_from_pdf',return_value=('研究正文',1))
    @patch('documents.views.Document.objects.create',side_effect=RuntimeError('db failed'))
    def test_failed_database_save_cleans_file(self, create, parse):
        self.assertEqual(self.upload().status_code,500)
        self.assertEqual(list(Path(self.tmp.name).rglob('*.pdf')),[])
    def test_bad_pdf_rejected(self):
        response=self.client.post('/documents/upload/',{'file':SimpleUploadedFile('fake.pdf',b'not pdf')},format='multipart')
        self.assertEqual(response.status_code,400)
    def test_reference_scope_rejects_another_users_document(self):
        other=get_user_model().objects.create_user(username='other')
        doc=Document.objects.create(user=other,title='private',file_name='private.pdf')
        with self.assertRaises(ValidationError):research_context(self.user,'query',[doc.id])
        with self.assertRaises(ValidationError):research_context(self.user,'query','not-a-list')
