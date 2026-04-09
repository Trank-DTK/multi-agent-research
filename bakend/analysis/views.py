import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from langchain_community.llms import Ollama
from .models import Dataset, AnalysisResult, DataVisualization
from .serializers import (
    DatasetSerializer, DatasetUploadSerializer, 
    AnalysisRequestSerializer, VisualizationRequestSerializer
)
from .services import DataAnalysisService
from agents.agent import get_ollama_base_url

class DatasetUploadView(APIView):
    """数据集上传接口"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = DatasetUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        
        uploaded_file = serializer.validated_data['file']
        name = serializer.validated_data.get('name', uploaded_file.name)
        description = serializer.validated_data.get('description', '')
        
        try:
            dataset, df = DataAnalysisService.save_dataset(
                request.user, uploaded_file, name, description
            )
            
            # 保存分析结果
            stats = DataAnalysisService.descriptive_statistics(df)
            
            # 生成AI洞察
            llm = Ollama(
                model="qwen2.5:7b",
                base_url=get_ollama_base_url(),
                temperature=0.5
            )
            insight = DataAnalysisService.generate_insight(df, stats, {}, llm)
            
            AnalysisResult.objects.create(
                dataset=dataset,
                analysis_type='descriptive',
                result_data=stats,
                insight=insight
            )
            
            return JsonResponse({
                'message': '上传成功',
                'dataset': DatasetSerializer(dataset).data,
                'preview': df.head(10).to_dict('records'),
                'columns': list(df.columns),
                'insight': insight[:500]
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class DatasetListView(APIView):
    """数据集列表接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        datasets = Dataset.objects.filter(user=request.user)
        serializer = DatasetSerializer(datasets, many=True)
        return JsonResponse(serializer.data, safe=False)


class DatasetDetailView(APIView):
    """数据集详情接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            df = DataAnalysisService.load_dataframe(dataset.file.path)
            
            return JsonResponse({
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'row_count': dataset.row_count,
                'column_count': dataset.column_count,
                'columns': list(df.columns),
                'preview': df.head(20).to_dict('records'),
                'uploaded_at': dataset.uploaded_at
            })
        except Dataset.DoesNotExist:
            return JsonResponse({'error': '数据集不存在'}, status=404)


class DatasetDeleteView(APIView):
    """删除数据集接口"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            dataset.delete()
            return JsonResponse({'message': '删除成功'})
        except Dataset.DoesNotExist:
            return JsonResponse({'error': '数据集不存在'}, status=404)


class DataAnalysisView(APIView):
    """数据分析接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            df = DataAnalysisService.load_dataframe(dataset.file.path)
            
            analysis_type = request.data.get('analysis_type', 'descriptive')
            columns = request.data.get('columns', [])
            
            llm = Ollama(
                model="qwen2.5:7b",
                base_url=get_ollama_base_url(),
                temperature=0.5
            )
            
            if analysis_type == 'descriptive':
                result = DataAnalysisService.descriptive_statistics(df, columns)
                insight = DataAnalysisService.generate_insight(df, result, {}, llm)
                
            elif analysis_type == 'correlation':
                result = DataAnalysisService.correlation_analysis(df, columns)
                if 'error' in result:
                    return JsonResponse({'error': result['error']}, status=400)
                stats = {'row_count': len(df), 'column_count': len(df.columns), 'statistics': {}}
                insight = DataAnalysisService.generate_insight(df, stats, result, llm)
                
            else:
                return JsonResponse({'error': '不支持的分析类型'}, status=400)
            
            # 保存分析结果
            analysis_result = AnalysisResult.objects.create(
                dataset=dataset,
                analysis_type=analysis_type,
                result_data=result,
                insight=insight
            )
            
            return JsonResponse({
                'result': result,
                'insight': insight,
                'analysis_id': analysis_result.id
            })
            
        except Dataset.DoesNotExist:
            return JsonResponse({'error': '数据集不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class DataVisualizationView(APIView):
    """数据可视化接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            df = DataAnalysisService.load_dataframe(dataset.file.path)
            
            chart_type = request.data.get('chart_type')
            x_column = request.data.get('x_column')
            y_column = request.data.get('y_column', '')
            title = request.data.get('title', '')
            
            if not chart_type or not x_column:
                return JsonResponse({'error': '缺少必要参数'}, status=400)
            
            chart_data = DataAnalysisService.prepare_chart_data(
                df, chart_type, x_column, y_column
            )
            
            # 保存可视化配置
            visualization = DataVisualization.objects.create(
                dataset=dataset,
                chart_type=chart_type,
                x_column=x_column,
                y_column=y_column,
                title=title,
                chart_config={'data': chart_data}
            )
            
            return JsonResponse({
                'chart_data': chart_data,
                'chart_type': chart_type,
                'title': title or f'{x_column} vs {y_column}' if y_column else f'{x_column}分布',
                'visualization_id': visualization.id
            })
            
        except Dataset.DoesNotExist:
            return JsonResponse({'error': '数据集不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)