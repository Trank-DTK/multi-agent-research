from django.urls import path
from .views import (ChatView, ChatStreamView,
                    ConversationListView,ConversationDetailView,
                    ConversationDeleteView)

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/stream/", ChatStreamView.as_view(), name="chat_stream"),
    path("chat/conversations/", ConversationListView.as_view(), name="conversation_list"),
    path('chat/conversations/<int:conv_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('chat/conversations/<int:conv_id>/delete/', ConversationDeleteView.as_view(), name='conversation_delete'),
]