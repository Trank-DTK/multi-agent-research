from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.provider_service import build_llm
from chat.models import Conversation, Message

TASKS = {
    'plan': '把研究目标拆解为可执行的阶段、任务、交付物与验证标准。先说明待确认的假设。',
    'hypothesis': '将研究问题转为可检验假设，明确自变量、因变量、对照与证伪条件。',
    'method': '帮助选择研究方法，比较备选方法的适用条件、成本、局限与复现步骤。',
    'review': '从论证、证据、可行性和表达四方面检查研究内容，给出具体修改建议。',
}
class AgentChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        message = str(request.data.get('message', '')).strip()
        task = request.data.get('task', 'plan')
        if not message or task not in TASKS:
            return JsonResponse({'error': '请输入问题并选择有效的科研任务'}, status=400)
        conversation = get_object_or_404(Conversation, pk=request.data['conversation_id'], user=request.user) if request.data.get('conversation_id') else Conversation.objects.create(user=request.user, title=message[:80])
        Message.objects.create(conversation=conversation, role='user', content=message)
        history = list(conversation.messages.order_by('-created_at')[:16])
        try:
            response = build_llm(request.user).chat([{'role': 'system', 'content': '你是科研任务助手。' + TASKS[task] + ' 不虚构引用、数据或已完成的实验。'}] + [{'role': m.role, 'content': m.content} for m in reversed(history)])
            Message.objects.create(conversation=conversation, role='assistant', content=response)
            conversation.save()
            return JsonResponse({'response': response, 'conversation_id': conversation.pk})
        except ValueError as exc:
            return JsonResponse({'error': str(exc), 'conversation_id': conversation.pk}, status=502)

class AgentResetView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, conv_id):
        get_object_or_404(Conversation, pk=conv_id, user=request.user)
        return JsonResponse({'message': '请新建对话以开始新的研究任务'})
