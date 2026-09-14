from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.provider_service import build_llm
from .collaboration_views import CollaborationResearchView

class CollaborationWithReviewView(CollaborationResearchView):
    with_review = True

class QuickEvaluateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        content = str(request.data.get('content', '')).strip()
        if not content:
            return JsonResponse({'error': '请输入待评审内容'}, status=400)
        try:
            text = build_llm(request.user).invoke('请评审以下研究内容，列出问题、依据和改进建议：\n' + content)
            return JsonResponse({'review': text})
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=502)
