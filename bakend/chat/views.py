import json
import os
import platform
from collections import deque
import threading
from django.http import JsonResponse,StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from langchain_ollama import OllamaLLM
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




#自定义流式回调，用于Django StreamingHttpResponse    (?)
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


            #初始化ollama模型
            try:
                llm = OllamaLLM(model="qwen2.5:7b", base_url=get_ollama_base_url(),temperature=0.7)
                response_text = llm.invoke(message)
            except Exception as e:
                # Ollama服务未运行或模型不存在
                response_text = f"抱歉，AI服务暂时不可用。请确保Ollama服务已运行并下载了qwen2.5:7b模型。\n\n错误详情：{str(e)}"
                # 即使AI服务不可用，也保存一条消息提示用户
                Message.objects.create(conversation=conversation, role='assistant', content=response_text)

            #保存AI回复（如果前面已保存则跳过）
            try:
                ai_message = Message.objects.get(conversation=conversation, role='assistant', content=response_text)
            except Message.DoesNotExist:
                ai_message = Message.objects.create(conversation=conversation, role='assistant', content=response_text)

            if conversation.title == "新对话":
                conversation.title = message[:20] + '...' if len(message) > 20 else message
                conversation.save()

            #同时保存到ChatHistory（兼容旧版）
            try:
                ChatHistory.objects.create(user=request.user, message=message, response=response_text, model_name="qwen2.5:7b")
            except:
                pass  # 如果ChatHistory表不存在或有问题，忽略错误

            return JsonResponse({"response": response_text,"model": "qwen2.5-7b",'conversation_id': conversation.id, 'message_id':ai_message.id})
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

    def get(self, request, conversation_id):
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
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


# (?)
class ChatStreamView(APIView):
    """流式聊天窗口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        message = serializer.validated_data['message']

        
        #创建一个队列用于存储生成的token
        from collections import deque
        token_queue = deque()

        #初始化ollama模型，添加自定义流式回调
        llm = OllamaLLM(
            model="qwen2.5:7b",
            base_url="http://localhost:11434",
            temperature=0.7,
            streaming=True,
            callbacks=[StreamingCallbackHandler(token_queue)],
        )

        #异步调用模型生成回复
        llm.invoke(message)

        #使用生成器函数流式返回token
        def generate():
            #在子线程中运行模型生成回复，主线程负责从队列中读取token并返回给前端
            import threading
            def run_model():
                try:
                    llm.invoke(message)
                except Exception as e:
                    token_queue.append(f"[ERROR: {str(e)}]")
                finally:
                    token_queue.append(None)  #生成结束标志
            thread = threading.Thread(target=run_model)
            thread.start()

            #不断从队列中取数据并发送
            while True:
                token = token_queue.popleft() if token_queue else None
                if token is None:  #生成结束
                    break
                if token:
                    # 以 Server-Sent Events 格式发送
                    yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingHttpResponse(generate(), content_type='text/event-stream')

            









