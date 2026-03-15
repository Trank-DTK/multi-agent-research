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


            #初始化ollama模型
            llm = OllamaLLM(model="qwen2.5:7b", base_url=get_ollama_base_url(),temperature=0.7)

            response_text = llm.invoke(message)

            #保存AI回复
            ai_message = Message.objects.create(conversation=conversation, role='assistant', content=response_text)

            if conversation.title == "新对话":
                conversation.title = message[:20] + '...' if len(message) > 20 else message
                conversation.save()

            #同时保存到ChatHistory（兼容旧版）
            ChatHistory.objects.create(user=request.user, message=message, response=response_text, model_name="qwen2.5:7b")

            

            return JsonResponse({"response": response_text,"model": "qwen2.5-7b",'conversation_id': conversation.id, 'message_id':ai_message.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            









