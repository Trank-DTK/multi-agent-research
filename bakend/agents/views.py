import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from langchain_classic.memory import ConversationBufferMemory
from .agent import create_agent
from chat.models import Conversation, Message

# 存储每个会话的Agent实例（简单内存缓存）
agent_instances = {}

class AgentChatView(APIView):
    """智能体聊天接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        message = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        
        if not message:
            return JsonResponse({'error': '消息不能为空'}, status=400)
        
        # 获取或创建对话
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return JsonResponse({'error': '对话不存在'}, status=404)
        else:
            conversation = Conversation.objects.create(
                user=user, 
                title=message[:20] + '...' if len(message) > 20 else message
            )
        
        # 保存用户消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )
        
        # 获取或创建Agent实例
        agent_key = f"agent_{conversation.id}_{user.id}"
        
        if agent_key not in agent_instances:
            # 从数据库加载历史消息构建记忆
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            previous_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('created_at')
            
            # 加载历史消息到记忆
            for msg in previous_messages:
                if msg.role == 'user':
                    memory.chat_memory.add_user_message(msg.content)
                elif msg.role == 'assistant':
                    memory.chat_memory.add_ai_message(msg.content)
            
            agent = create_agent(memory=memory, verbose=False)
            agent_instances[agent_key] = agent
        else:
            agent = agent_instances[agent_key]
        
        try:
            # 运行Agent
            response = agent.run(message)
            
            # 保存助手回复
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=response
            )
            
            return JsonResponse({
                'response': response,
                'conversation_id': conversation.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AgentResetView(APIView):
    """重置Agent对话（清空记忆）"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, conv_id):
        user = request.user
        agent_key = f"agent_{conv_id}_{user.id}"
        
        if agent_key in agent_instances:
            del agent_instances[agent_key]
        
        return JsonResponse({'message': '对话已重置'})