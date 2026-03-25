# 多智能体协作API
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .orchestrator import TaskOrchestrator
from .literature_agent import create_literature_agent
from .experiment_agent import create_experiment_agent
from documents.services import VectorService
from chat.models import Conversation, Message

# 存储编排器实例
orchestrator_instances = {}

class CollaborationResearchView(APIView):
    """多智能体协作研究接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        question = request.data.get('question')
        conversation_id = request.data.get('conversation_id')

        if not question:
            return JsonResponse({'error': '研究问题不能为空'}, status=400)

        # 获取或创建对话
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return JsonResponse({'error': '对话不存在'}, status=404)
        else:
            conversation = Conversation.objects.create(
                user=user,
                title=question[:20] + '...' if len(question) > 20 else question
            )

        # 保存用户消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=question
        )

        # 获取或创建编排器（使用用户ID作为key）
        orchestrator_key = f"orchestrator_{user.id}"
        if orchestrator_key not in orchestrator_instances:
            orchestrator = TaskOrchestrator(user)

            # 创建智能体
            vector_service = VectorService()
            # 使用False关闭verbose，减少输出和内存
            literature_agent = create_literature_agent(user, memory=None, verbose=False)
            experiment_agent = create_experiment_agent(user, vector_service, memory=None, verbose=False)

            # 注册智能体
            orchestrator.register_agents(
                literature_agent=literature_agent,
                experiment_agent=experiment_agent
            )

            orchestrator_instances[orchestrator_key] = orchestrator
        else:
            orchestrator = orchestrator_instances[orchestrator_key]

        # 执行后清理已完成的orchestrator实例，避免内存泄漏
        if len(orchestrator_instances) > 5:
            # 保留最近5个，清理其他
            sorted_keys = sorted(orchestrator_instances.keys())
            for key in sorted_keys[:-5]:
                del orchestrator_instances[key]

        # 同步执行研究任务
        try:
            results = orchestrator.execute_research_task(question, conversation)

            # 保存助手回复
            final_report = results.get('final_report', '')
            if final_report:
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=final_report[:2000]  # 限制长度
                )

            return JsonResponse({
                'response': final_report[:1000],
                'conversation_id': conversation.id,
                'results': {
                    'literature_review': results.get('literature_review', '')[:500],
                    'experiment_design': results.get('experiment_design', '')[:500]
                }
            })

        except Exception as e:
            import sys, traceback
            traceback.print_exc(file=sys.stderr)
            return JsonResponse({'error': str(e)}, status=500)


class CollaborationStatusView(APIView):
    """查看协作任务状态"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        from .orchestrator import Task
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            steps = task.steps.all()
            
            return JsonResponse({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'result': task.result[:500] if task.result else '',
                'created_at': task.created_at,
                'steps': [{
                    'agent': s.agent_name,
                    'action': s.action,
                    'status': s.status,
                    'output': s.output_data[:200]
                } for s in steps]
            })
        except Task.DoesNotExist:
            return JsonResponse({'error': '任务不存在'}, status=404)