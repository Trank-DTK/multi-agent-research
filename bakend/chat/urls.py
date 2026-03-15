from django.urls import path
from .views import ChatView, ChatStreamView

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/stream/", ChatStreamView.as_view(), name="chat_stream"),
]