from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.provider_service import build_llm
from accounts.streaming import stream_response
from .models import Dataset
from .services import DataAnalysisService

class AnalysisAgentChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
        message = str(request.data.get('message', '')).strip()
        if not message:
            return JsonResponse({'error': '消息不能为空'}, status=400)
        try:
            df = DataAnalysisService.load_dataframe(dataset.file.path)
            summary = df.describe(include='all').to_string()[:16000]
            preview = df.head(10).to_string(index=False)[:8000]
            messages = [{'role': 'system', 'content': '你是科研数据分析助手。依据给定预览和统计摘要回答，不把样本预览当作完整数据，不虚构已运行的检验。需要进一步计算时明确说明。'}, {'role': 'user', 'content': f'数据集：{dataset.name}，{len(df)} 行\n统计摘要：\n{summary}\n前10行：\n{preview}\n问题：{message}'}]
            llm = build_llm(request.user)
            if request.data.get('stream') is True:
                return stream_response(llm, messages)
            response = llm.chat(messages)
            return JsonResponse({'response': response, 'dataset_id': dataset_id})
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        except Exception:
            return JsonResponse({'error': '无法读取数据集，请检查文件或重新上传'}, status=500)
