"""Separate model generation budgets from ordinary workspace navigation."""
from rest_framework.throttling import SimpleRateThrottle

MODEL_VIEWS = {
    'ChatView', 'ChatStreamView', 'LiteratureAgentView', 'AnalysisAgentChatView',
    'AgentChatView', 'CollaborationResearchView', 'CollaborationReviewView', 'CollaborationWithReviewView', 'QuickEvaluateView',
    'GenerateOutlineView', 'WriteSectionView', 'PolishTextView',
    'GenerateAbstractView', 'WritingAgentChatView', 'DataAnalysisView', 'ProviderTestView',
}

def uses_model(request, view):
    if request.method != 'POST':
        return False
    name = type(view).__name__
    if name == 'PaperCreateView':
        return bool(request.data.get('topic'))
    if name == 'WriteSectionView' and request.data.get('generate') is False:
        return False
    return name in MODEL_VIEWS

class BurstRateThrottle(SimpleRateThrottle):
    scope = 'burst'
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated or not uses_model(request, view):
            return None
        return f'model_burst_v2_{request.user.id}_{type(view).__name__}'

class SustainedRateThrottle(SimpleRateThrottle):
    scope = 'sustained'
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated or not uses_model(request, view):
            return None
        return f'model_sustained_v2_{request.user.id}'
