from rest_framework import serializers
from .models import Document, DocumentChunk

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file_name', 'file_size', 'page_count', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class DocumentUploadSerializer(serializers.Serializer):
    """文档上传序列化器"""
    title = serializers.CharField(max_length=500, required=False)
    file = serializers.FileField()


class DocumentSearchSerializer(serializers.Serializer):
    """文档检索序列化器"""
    query = serializers.CharField(max_length=1000)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)