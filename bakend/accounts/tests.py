from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from rest_framework.test import APIClient
from .models import ModelProvider
from .provider_service import build_llm, encrypt_key, decrypt_key, ProviderLLM, validate_base_url

class ProviderTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='owner')
        self.other = get_user_model().objects.create_user(username='other')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.payload = {'name':'Test','protocol':'openai','base_url':'https://example.com/v1','model':'test-model','api_key':'test-secret-key'}
    def create(self):
        response = self.client.post('/providers/', self.payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data
    def test_key_is_encrypted_and_never_returned(self):
        data = self.create()
        self.assertTrue(data['is_default'])
        self.assertNotIn('api_key', data)
        stored = ModelProvider.objects.get(pk=data['id'])
        self.assertNotIn('test-secret-key', stored.encrypted_api_key)
        self.assertEqual(decrypt_key(stored.encrypted_api_key), 'test-secret-key')
        self.assertNotIn('test-secret-key', str(self.client.get('/providers/').data))
    def test_other_users_cannot_read_update_delete_or_test(self):
        data = self.create()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/providers/').data, [])
        self.assertEqual(self.client.patch(f"/providers/{data['id']}/", {'model':'stolen'}).status_code,404)
        self.assertEqual(self.client.delete(f"/providers/{data['id']}/").status_code,404)
        with patch('accounts.provider_views.build_llm') as build:
            self.assertEqual(self.client.post(f"/providers/{data['id']}/test/").status_code,404)
            build.assert_not_called()
    def test_switching_default_and_deleting_default(self):
        first = self.create()
        second = self.create()
        response = self.client.patch(f"/providers/{second['id']}/", {'is_default':True}, format='json')
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(ModelProvider.objects.filter(user=self.user,is_default=True).count(),1)
        self.assertEqual(build_llm(self.user).model,'test-model')
        self.client.delete(f"/providers/{second['id']}/")
        self.assertTrue(ModelProvider.objects.get(pk=first['id']).is_default)
    def test_edit_retains_key_but_new_host_requires_explicit_key(self):
        data=self.create()
        endpoint=f"/providers/{data['id']}/"
        self.assertEqual(self.client.patch(endpoint,{'model':'another'},format='json').status_code,200)
        self.assertEqual(decrypt_key(ModelProvider.objects.get(pk=data['id']).encrypted_api_key),'test-secret-key')
        self.assertEqual(self.client.patch(endpoint,{'base_url':'https://other.example/v1'},format='json').status_code,400)
        self.assertEqual(self.client.patch(endpoint,{'base_url':'https://other.example/v1','api_key':''},format='json').status_code,200)
    def test_local_provider_without_key(self):
        self.payload.update(protocol='ollama',base_url='http://localhost:11434',api_key='')
        data=self.create()
        self.assertFalse(data['has_api_key'])
    def test_unauthenticated_access_is_denied(self):
        self.client = APIClient()
        self.assertIn(self.client.get('/providers/').status_code,[401,403])

class ProviderTransportTests(SimpleTestCase):
    @patch('accounts.provider_service.requests.post')
    def test_openai_and_ollama_protocols(self, post):
        post.return_value=Mock(status_code=200)
        post.return_value.json.return_value={'choices':[{'message':{'content':'ok'}}]}
        llm=ProviderLLM(base_url='https://example.com/v1/',model='custom',api_key='secret')
        self.assertEqual(llm.invoke('hello'),'ok')
        args=post.call_args
        self.assertEqual(args.args[0],'https://example.com/v1/chat/completions')
        self.assertFalse(args.kwargs['allow_redirects'])
        self.assertEqual(args.kwargs['headers']['Authorization'],'Bearer secret')
        post.return_value.json.return_value={'message':{'content':'local'}}
        local=ProviderLLM(base_url='http://localhost:11434',model='local',protocol='ollama')
        self.assertEqual(local.invoke('hello'),'local')
        self.assertNotIn('Authorization',post.call_args.kwargs['headers'])
        self.assertTrue(post.call_args.args[0].endswith('/api/chat'))
    @patch('accounts.provider_service.requests.post')
    def test_provider_error_does_not_echo_response_secret(self, post):
        post.return_value=Mock(status_code=401,text='secret-key')
        with self.assertRaisesRegex(ValueError,'HTTP 401') as error:
            ProviderLLM(base_url='https://example.com/v1',model='custom').invoke('hi')
        self.assertNotIn('secret-key',str(error.exception))
    def test_url_validation(self):
        for url in ['file:///etc/passwd','http://user:pass@example.com','http://169.254.169.254','https://example.com?key=secret']:
            with self.assertRaises(ValueError): validate_base_url(url)


class ResearchScopeTests(TestCase):
    def test_research_uses_selected_sources_and_review_is_optional(self):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from agents.collaboration_views import CollaborationResearchView
        from documents.models import Document, DocumentChunk
        user=get_user_model().objects.create_user(username='researcher')
        selected=Document.objects.create(user=user,title='Selected evidence',file_name='selected.pdf')
        excluded=Document.objects.create(user=user,title='Excluded evidence',file_name='excluded.pdf')
        DocumentChunk.objects.create(document=selected,chunk_index=0,content='SELECTED_EVIDENCE')
        DocumentChunk.objects.create(document=excluded,chunk_index=0,content='EXCLUDED_EVIDENCE')
        for review, calls in [(False,3),(True,4)]:
            request=APIRequestFactory().post('/research/',{'question':'research question','document_ids':[selected.pk],'with_review':review},format='json')
            force_authenticate(request,user=user)
            with patch('agents.collaboration_views.build_llm') as build:
                build.return_value.chat.return_value='Detailed research result'
                response=CollaborationResearchView.as_view()(request)
                self.assertEqual(response.status_code,200,response.content)
                self.assertEqual(build.return_value.chat.call_count,calls)
                prompts=str(build.return_value.chat.call_args_list)
                self.assertIn('SELECTED_EVIDENCE',prompts)
                self.assertNotIn('EXCLUDED_EVIDENCE',prompts)
                build.assert_called_once_with(user)
