from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Paper, PaperSection

class SectionPersistenceTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="writer")
        self.paper = Paper.objects.create(user=self.owner, title="Research")
        self.section = PaperSection.objects.create(paper=self.paper, title="Methods", section_type="custom")
        self.url = f"/papers/{self.paper.pk}/sections/{self.section.pk}/"
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_save_and_delete_persist(self):
        response = self.client.patch(self.url, {"content": "Revised evidence", "title": "Results"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.section.refresh_from_db()
        self.assertEqual(self.section.content, "Revised evidence")
        self.assertEqual(self.section.title, "Results")
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertFalse(PaperSection.objects.exists())

    def test_other_user_cannot_edit_or_delete(self):
        self.client.force_authenticate(get_user_model().objects.create_user(username="other"))
        self.assertEqual(self.client.patch(self.url, {"content": "overwrite"}).status_code, 404)
        self.assertEqual(self.client.delete(self.url).status_code, 404)
        self.assertTrue(PaperSection.objects.filter(pk=self.section.pk).exists())
