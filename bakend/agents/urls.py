from django.urls import path
from agents.views import AgentChatView, AgentResetView

urlpatterns = [
    path('agent/chat/', AgentChatView.as_view(), name='agent_chat'),
    path('agent/reset/<int:conv_id>/', AgentResetView.as_view(), name='agent_reset'),
]