import json
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from .views import ChatStreamView
from .models import Conversation, Message

class StreamTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='stream-user')

    def request(self, payload):
        request = APIRequestFactory().post('/chat/stream/', payload, format='json', HTTP_ACCEPT='text/event-stream, application/json')
        force_authenticate(request, user=self.user)
        return ChatStreamView.as_view()(request)

    @patch('chat.views.build_llm')
    def test_incremental_output_persistence_and_history(self, build):
        build.return_value.stream_chat.return_value = iter(['first', 'second'])
        response = self.request({'message':'hello'})
        self.assertTrue(response.streaming)
        self.assertEqual(response['X-Accel-Buffering'], 'no')
        iterator = iter(response.streaming_content)
        self.assertIn(b'conversation_id', next(iterator))
        self.assertIn(b'first', next(iterator))
        self.assertFalse(Message.objects.filter(role='assistant').exists())
        self.assertIn(b'[DONE]', b''.join(iterator))
        self.assertEqual(Message.objects.get(role='assistant').content, 'firstsecond')
        build.return_value.stream_chat.return_value = iter(['reply'])
        b''.join(self.request({'message':'followup', 'conversation_id':Conversation.objects.get().pk}).streaming_content)
        prompt = build.return_value.stream_chat.call_args.args[0]
        self.assertEqual([item['content'] for item in prompt], ['hello', 'firstsecond', 'followup'])

    @patch('chat.views.build_llm')
    def test_stream_error_keeps_partial_output_without_saving_as_complete(self, build):
        def broken():
            yield 'partial'
            raise ValueError('connection interrupted')
        build.return_value.stream_chat.return_value = broken()
        data = b''.join(self.request({'message':'hello'}).streaming_content)
        self.assertIn(b'partial', data)
        self.assertIn(b'error', data)
        self.assertNotIn(b'[DONE]', data)
        self.assertFalse(Message.objects.filter(role='assistant').exists())

    def test_other_users_conversation_is_rejected(self):
        other = get_user_model().objects.create_user(username='private')
        conv = Conversation.objects.create(user=other, title='private')
        self.assertEqual(self.request({'message':'hello', 'conversation_id':conv.pk}).status_code,404)

    @patch('agents.literature_views.build_llm')
    def test_literature_stream_uses_selected_references(self, build):
        from agents.literature_views import LiteratureAgentView
        from documents.models import Document, DocumentChunk
        doc = Document.objects.create(user=self.user, title='Evidence', file_name='evidence.pdf')
        DocumentChunk.objects.create(document=doc, chunk_index=0, content='SELECTED RESEARCH EVIDENCE')
        request = APIRequestFactory().post('/literature/chat/', {'message':'research', 'document_ids':[doc.pk], 'stream':True}, format='json', HTTP_ACCEPT='text/event-stream, application/json')
        force_authenticate(request, user=self.user)
        build.return_value.stream_chat.return_value = iter(['one', 'two'])
        response = LiteratureAgentView.as_view()(request)
        self.assertIn(b'[DONE]', b''.join(response.streaming_content))
        self.assertIn('SELECTED RESEARCH EVIDENCE', str(build.return_value.stream_chat.call_args))
