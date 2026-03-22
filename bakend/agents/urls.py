from django.urls import path
from agents.views import AgentChatView, AgentResetView
from .literature_views import LiteratureAgentView,LiteratureAgentResetView

urlpatterns = [
    path('agent/chat/', AgentChatView.as_view(), name='agent_chat'),
    path('agent/reset/<int:conv_id>/', AgentResetView.as_view(), name='agent_reset'),
    path('literature/chat/',LiteratureAgentView.as_view(),name='literature_chat'),
    path('literature/reset/',LiteratureAgentResetView.as_view(),name='literature_reset'),
]