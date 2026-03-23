import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer, DocumentSearchSerializer
from .services import PDFParseService, VectorService

class DocumentUploadView(APIView):
    """文档上传接口"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        
        uploaded_file = serializer.validated_data['file']
        title = serializer.validated_data.get('title', uploaded_file.name)
        
        # 保存文件
        file_path = default_storage.save(f'documents/{request.user.id}/{uploaded_file.name}', uploaded_file)
        full_path = default_storage.path(file_path)
        
        try:
            # 解析PDF
            text, page_count = PDFParseService.extract_text_from_pdf(full_path)
            
            if not text.strip():
                return JsonResponse({'error': 'PDF中没有提取到文本'}, status=400)
            
            # 创建文档记录
            document = Document.objects.create(
                user=request.user,
                title=title,
                file=file_path,
                file_name=uploaded_file.name,
                file_size=uploaded_file.size,
                page_count=page_count
            )
            
            # 文本分块
            chunks = PDFParseService.split_text(text)
            
            # 生成向量并存储
            vector_service = VectorService()
            vector_service.create_chunks_with_vectors(document, chunks)
            
            return JsonResponse({
                'message': '上传成功',
                'document': DocumentSerializer(document).data,
                'chunk_count': len(chunks)
            })
            
        except Exception as e:
            # 出错时删除已保存的文件
            if os.path.exists(full_path):
                os.remove(full_path)
            return JsonResponse({'error': str(e)}, status=500)


class DocumentListView(APIView):
    """文档列表接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        documents = Document.objects.filter(user=request.user)
        serializer = DocumentSerializer(documents, many=True)
        return JsonResponse(serializer.data, safe=False)


class DocumentDeleteView(APIView):
    """删除文档接口"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, doc_id):
        try:
            document = Document.objects.get(id=doc_id, user=request.user)
            document.delete()  # 模型中的delete方法会删除文件
            return JsonResponse({'message': '删除成功'})
        except Document.DoesNotExist:
            return JsonResponse({'error': '文档不存在'}, status=404)


class DocumentSearchView(APIView):
    """文档检索接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = DocumentSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        
        query = serializer.validated_data['query']
        top_k = serializer.validated_data['top_k']
        
        vector_service = VectorService()
        results = vector_service.search_similar(query, request.user, top_k)
        
        return JsonResponse({
            'query': query,
            'results': results
        })