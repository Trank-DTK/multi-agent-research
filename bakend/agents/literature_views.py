# 文献助手的API
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .literature_agent import create_literature_agent

# 存储Agent实例
agent_instances = {}

class LiteratureAgentView(APIView):
    """文献助手智能体接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        message = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        
        if not message:
            return JsonResponse({'error': '消息不能为空'}, status=400)
        
        # 使用用户ID作为会话key（简化版）
        agent_key = f"literature_{user.id}_{conversation_id}" if conversation_id else f"literature_{user.id}"
        
        if agent_key not in agent_instances:
            agent = create_literature_agent(user, verbose=False)  # 创建新实例
            agent_instances[agent_key] = agent   # 缓存
        else:
            agent = agent_instances[agent_key]   # 复用缓存
        
        try:
            response = agent.run(message)
            return JsonResponse({
                'response': response,
                'conversation_id': conversation_id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class LiteratureAgentResetView(APIView):
    """重置文献助手对话"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        agent_key = f"literature_{user.id}"
        
        if agent_key in agent_instances:
            del agent_instances[agent_key]    #删除缓存的Agent
        
        return JsonResponse({'message': '对话已重置'})