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
        
        from django.db import transaction
        from .models import DocumentChunk
        file_path = None
        try:
            file_path = default_storage.save(f'documents/{request.user.id}/{uploaded_file.name}', uploaded_file)
            text, page_count = PDFParseService.extract_text_from_pdf(default_storage.path(file_path))
            if not text.strip():
                default_storage.delete(file_path)
                return JsonResponse({'error': 'PDF 没有可提取的文本。扫描版请先进行 OCR 识别后再上传。'}, status=400)
            chunks = PDFParseService.split_text(text)
            with transaction.atomic():
                document = Document.objects.create(user=request.user, title=title or uploaded_file.name, file=file_path, file_name=uploaded_file.name, file_size=uploaded_file.size, page_count=page_count)
                DocumentChunk.objects.bulk_create([DocumentChunk(document=document, chunk_index=i, content=chunk) for i, chunk in enumerate(chunks)])
            return JsonResponse({'message': '上传成功，文本已可用于检索与研究', 'document': DocumentSerializer(document).data, 'chunk_count': len(chunks)}, status=201)
        except Exception:
            if file_path:
                default_storage.delete(file_path)
            return JsonResponse({'error': '文献保存失败，请确认 PDF 未损坏，并检查数据库迁移和文件存储权限。'}, status=500)


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