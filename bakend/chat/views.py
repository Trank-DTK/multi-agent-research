import json
from django.http import JsonResponse,StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from langchain_ollama import OllamaLLM
from langchain_core.callbacks import BaseCallbackHandler
from .serializers import ChatMessageSerializer


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

        try:
            #初始化ollama模型
            llm = OllamaLLM(model="qwen2.5:7b", base_url="http://localhost:11434",temperature=0.7)

            response = llm.invoke(message)

            #这里可以将来保存对话到数据库
            # ChatHistory.objects.create(user=request.user, message=message, response=response)

            return JsonResponse({"response": response,"model": "qwen2.5-7b"})
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

            









