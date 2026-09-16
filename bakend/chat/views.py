from accounts.provider_service import build_llm
import json
import os
import platform
from collections import deque
from django.http import JsonResponse,StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from langchain_core.callbacks import BaseCallbackHandler
from .serializers import ChatMessageSerializer
from .models import ChatHistory,Message,Conversation


#获取ollama地址（兼容Docker和本地）
def get_ollama_base_url():
    """根据运行环境返回正确的ollama地址"""
    if os.path.exists('/.dockerenv'):
        #Windows/Mac Docker环境
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            return os.environ.get('OLLAMA_BASE_URL',"http://host.docker.internal:11434")
        #Linux Docker环境
        else:
            return os.environ.get('OLLAMA_BASE_URL',"http://172.17.0.1:11434")
    #本地运行
    else:
        return os.environ.get('OLLAMA_BASE_URL',"http://localhost:11434")




#自定义流式回调，用于Django StreamingHttpResponse   
class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """每当模型生成新token时调用，将token写入队列"""
        self.queue.append(token)


class ChatView(APIView):
    """普通聊天窗口（非流式）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        message = serializer.validated_data['message']
        conversation_id = request.data.get('conversation_id')

        try:
            #获取或创建会话
            if conversation_id:
                conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
            else:
                #创建新会话，临时标题稍后更新
                conversation = Conversation.objects.create(user=request.user,title="新对话")

            user_message = Message.objects.create(conversation=conversation, role='user', content=message)


            llm = build_llm(request.user)
            try:
                history = list(conversation.messages.order_by('-created_at')[:20])
                response_text = llm.chat([{'role': m.role, 'content': m.content} for m in reversed(history)])
            except Exception as e:
                # Ollama服务未运行或模型不存在
                response_text = f"抱歉，AI服务暂时不可用。请到设置检查模型供应商、地址和模型名称。\n\n错误详情：{str(e)}"

            ai_message = Message.objects.create(conversation=conversation, role='assistant', content=response_text)

            if conversation.title == "新对话":
                conversation.title = message[:20] + '...' if len(message) > 20 else message
            conversation.save()

            #同时保存到ChatHistory（兼容旧版）
            try:
                ChatHistory.objects.create(user=request.user, message=message, response=response_text, model_name=llm.model)
            except:
                pass  # 如果ChatHistory表不存在或有问题，忽略错误

            return JsonResponse({"response": response_text,"model": llm.model,'conversation_id': conversation.id, 'message_id':ai_message.id})
        except Exception as e:
            return JsonResponse({"error": "服务器内部错误，请稍后再试。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationListView(APIView):
    """获取用户的对话列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(user=request.user)[:20]  #只返回最近20条会话
        data = [{
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": conv.messages.count(),
            "preview":conv.messages.first().content[:50] if conv.messages.exists() else ""  #预览第一条消息的前50个字符
        } for conv in conversations
        ]
        
        return JsonResponse(data, safe=False)
    
class ConversationDetailView(APIView):
    """获取单个会话的消息列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conv_id):
        try:
            conversation = get_object_or_404(Conversation, id=conv_id, user=request.user)
            messages = conversation.messages.all()
            data = [{
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            } for msg in messages]
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=404)
    

class ConversationDeleteView(APIView):
    """删除会话"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        conversation_id = kwargs.get('conv_id')  # 从kwargs中获取conv_id
        try:
            print(f"正在删除会话，ID: {conversation_id}, 用户: {request.user.username}")
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
            print(f"找到会话: {conversation.title}, 消息数量: {conversation.messages.count()}")
            conversation.delete()
            print(f"会话 {conversation_id} 删除成功")
            return JsonResponse({"message": "删除成功"},status=200)
        except Exception as e:
            print(f"删除会话失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=404)



class ChatStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from accounts.streaming import stream_response
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        conversation_id = request.data.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user) if conversation_id else None
        try:
            llm = build_llm(request.user)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        if conversation is None:
            conversation = Conversation.objects.create(user=request.user, title=message[:20])
        Message.objects.create(conversation=conversation, role='user', content=message)
        history = list(conversation.messages.order_by('-created_at', '-id')[:20])
        prompt = [{'role': item.role, 'content': item.content} for item in reversed(history)]
        def save_answer(text):
            answer = Message.objects.create(conversation=conversation, role='assistant', content=text)
            conversation.save()
            return {'message_id': answer.id}
        return stream_response(llm, prompt, {'conversation_id': conversation.id}, save_answer)
