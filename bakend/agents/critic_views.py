# 评审API视图
import time
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .feedback_orchestrator import FeedbackOrchestrator
from .literature_agent import create_literature_agent
from .experiment_agent import create_experiment_agent
from .critic_agent import CriticService
from .audit_middleware import AuditLogService
from ..documents.services import VectorService
from ..chat.models import Conversation, Message

orchestrator_instances = {}

class CollaborationWithReviewView(APIView):
    """带评审的协作研究接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        start_time = time.time()
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
        
        # 获取或创建编排器
        orchestrator_key = f"feedback_orchestrator_{user.id}"
        if orchestrator_key not in orchestrator_instances:
            orchestrator = FeedbackOrchestrator(user)
            
            vector_service = VectorService()
            literature_agent = create_literature_agent(user, verbose=False)
            experiment_agent = create_experiment_agent(user, vector_service, verbose=False)
            
            orchestrator.register_agents(
                literature_agent=literature_agent,
                experiment_agent=experiment_agent
            )
            
            orchestrator_instances[orchestrator_key] = orchestrator
        else:
            orchestrator = orchestrator_instances[orchestrator_key]

        # 清理已完成的orchestrator实例，避免内存泄漏（保留最近5个）
        if len(orchestrator_instances) > 5:
            sorted_keys = sorted(orchestrator_instances.keys())
            for key in sorted_keys[:-5]:
                del orchestrator_instances[key]

        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    orchestrator.execute_research_task_with_feedback(question, conversation)
                )
            finally:
                loop.close()
            
            # 保存助手回复
            final_report = results.get('final_report', '')
            evaluation = results.get('evaluation', {})
            
            # 添加评审信息到回复
            review_summary = f"""
--- 评审报告 ---
综合评分: {evaluation.get('overall_score', 'N/A')}/10
是否通过: {'✅ 是' if evaluation.get('passed') else '❌ 否'}

改进建议:
{chr(10).join(['- ' + s for s in evaluation.get('suggestions', [])[:5]])}
"""
            
            full_response = final_report + "\n\n" + review_summary
            
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=full_response[:2000]
            )
            
            # 记录审计
            AuditLogService.log(
                user=user,
                action_type='workflow_execution',
                action_name='带评审的研究任务',
                input_data=question[:500],
                output_data=f"评分: {evaluation.get('overall_score')}, 通过: {evaluation.get('passed')}",
                duration_ms=int((time.time() - start_time) * 1000),
                request=request
            )
            
            return JsonResponse({
                'response': full_response[:1000],
                'conversation_id': conversation.id,
                'evaluation': {
                    'overall_score': evaluation.get('overall_score', 0),
                    'passed': evaluation.get('passed', False),
                    'suggestions': evaluation.get('suggestions', [])[:5],
                    'dimensions': {
                        'literature_review': evaluation.get('dimensions', {}).get('literature_review', {}).get('score', 0),
                        'experiment_design': evaluation.get('dimensions', {}).get('experiment_design', {}).get('score', 0),
                        'consistency': evaluation.get('dimensions', {}).get('consistency', {}).get('score', 0),
                        'feasibility': evaluation.get('dimensions', {}).get('feasibility', {}).get('score', 0),
                    }
                },
                'improved': results.get('improved', False)
            })
            
        except Exception as e:
            import traceback
            AuditLogService.log(
                user=user,
                action_type='error',
                action_name='研究任务失败',
                input_data=question[:500],
                error_message=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                request=request,
                status='failed'
            )
            return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


class QuickEvaluateView(APIView):
    """快速评审接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        content = request.data.get('content', '')
        if not content:
            return JsonResponse({'error': '内容不能为空'}, status=400)
        
        critic = CriticService()
        evaluation = critic.evaluate_quality(content)
        
        return JsonResponse(evaluation)