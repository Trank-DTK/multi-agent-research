import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.provider_service import build_llm
from documents.context import research_context
from chat.models import Conversation, Message

class CollaborationResearchView(APIView):
    permission_classes = [IsAuthenticated]
    with_review = False
    def post(self, request):
        question = str(request.data.get('question', '')).strip()
        if not question or len(question) > 10000:
            return JsonResponse({'error': '研究问题不能为空，且不能超过 10000 字'}, status=400)
        ids = request.data.get('document_ids', [])
        context = research_context(request.user, question, ids)
        conversation = get_object_or_404(Conversation, pk=request.data['conversation_id'], user=request.user) if request.data.get('conversation_id') else Conversation.objects.create(user=request.user, title=question[:80])
        Message.objects.create(conversation=conversation, role='user', content=question)
        try:
            llm = build_llm(request.user)
            def run(role, content):
                return llm.chat([{'role': 'system', 'content': role + '。请用中文，区分已有证据与研究建议，不虚构引用或实验结果。'}, {'role': 'user', 'content': content}])
            literature = run('你是文献研究员，分析证据、研究空白和局限', context + '\n研究问题：' + question)
            experiment = run('你是实验设计师，提出假设、变量、对照、评估指标和可复现步骤', question + '\n参考证据：' + literature)
            report = run('你是研究负责人，整合成结构清晰的研究方案，保留文献 ID 引用', question + '\n文献分析：' + literature + '\n实验方案：' + experiment)
            result = {'response': report, 'conversation_id': conversation.pk, 'results': {'literature_review': literature, 'experiment_design': experiment}, 'document_ids': ids}
            if self.with_review or request.data.get('with_review') is True:
                review = run('你是严格的科研评审员，指出证据、可行性、创新性和方法上的具体问题，并给出可执行的改进建议', context + '\n研究方案：' + report)
                result['review'] = review
            Message.objects.create(conversation=conversation, role='assistant', content=report + ('\n\n评审意见：\n' + result['review'] if result.get('review') else ''))
            conversation.save()
            return JsonResponse(result)
        except ValueError as exc:
            return JsonResponse({'error': str(exc), 'conversation_id': conversation.pk}, status=502)

class CollaborationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, task_id):
        from .models import Task
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        return JsonResponse({'id': task.pk, 'status': task.status, 'result': task.result})
