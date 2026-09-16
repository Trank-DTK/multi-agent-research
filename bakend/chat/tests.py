from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Conversation, Message
from .views import ChatView


class ChatMessagePersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="research-test")
        self.conversation = Conversation.objects.create(user=self.user, title="Existing research")
        self.factory = APIRequestFactory()

    def send(self):
        request = self.factory.post("/api/chat/", {
            "sender": "user", "message": "Explain the result",
            "conversation_id": self.conversation.pk,
        }, format="json")
        force_authenticate(request, user=self.user)
        return ChatView.as_view()(request)

    @patch("chat.views.build_llm")
    def test_identical_replies_are_saved_for_each_turn(self, llm):
        llm.return_value.model="test-model"
        llm.return_value.chat.return_value = "Same answer"
        before = self.conversation.updated_at
        self.assertEqual(self.send().status_code, 200)
        self.assertEqual(self.send().status_code, 200)
        self.assertEqual(Message.objects.filter(conversation=self.conversation, role="assistant").count(), 2)
        self.conversation.refresh_from_db()
        self.assertGreater(self.conversation.updated_at, before)

    @patch("chat.views.build_llm")
    def test_repeated_model_failures_do_not_break_message_saving(self, llm):
        llm.return_value.model="test-model"
        llm.return_value.chat.side_effect = RuntimeError("Model unavailable")
        self.assertEqual(self.send().status_code, 200)
        self.assertEqual(self.send().status_code, 200)
        self.assertEqual(Message.objects.filter(conversation=self.conversation).count(), 4)
