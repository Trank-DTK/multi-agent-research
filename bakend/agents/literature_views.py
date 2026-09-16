from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.provider_service import build_llm
from accounts.streaming import stream_response
from documents.context import research_context
from documents.models import Document

class LiteratureAgentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        message = str(request.data.get('message', '')).strip()
        if not message:
            return JsonResponse({'error': '请输入文献问题'}, status=400)
        ids = request.data.get('document_ids', list(Document.objects.filter(user=request.user).values_list('id', flat=True)[:30]))
        context = research_context(request.user, message, ids)
        if not ids:
            return JsonResponse({'error': '请先上传并选择参考文献'}, status=400)
        try:
            messages = [{'role': 'system', 'content': '你是科研文献助手。依据提供的摘录回答，标出引用，证据不足时明确说明。'}, {'role': 'user', 'content': context + '\n\n问题：' + message}]
            llm = build_llm(request.user)
            if request.data.get('stream') is True:
                return stream_response(llm, messages)
            response = llm.chat(messages)
            return JsonResponse({'response': response})
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

class LiteratureAgentResetView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return JsonResponse({'message': '对话已重置'})
