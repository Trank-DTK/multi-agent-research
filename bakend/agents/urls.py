from django.urls import path
from agents.views import AgentChatView, AgentResetView
from .literature_views import LiteratureAgentView,LiteratureAgentResetView
from .collaboration_views import CollaborationResearchView,CollaborationStatusView

urlpatterns = [
    path('agent/chat/', AgentChatView.as_view(), name='agent_chat'),
    path('agent/reset/<int:conv_id>/', AgentResetView.as_view(), name='agent_reset'),
    path('literature/chat/',LiteratureAgentView.as_view(),name='literature_chat'),
    path('literature/reset/',LiteratureAgentResetView.as_view(),name='literature_reset'),
    path('collaboration/research/',CollaborationResearchView.as_view(),name='collaboration_research'),
    path('collaboration/status/<int:task_id>/',CollaborationStatusView.as_view(),name='collaboration_status'),
]