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
    def validate_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError('仅支持 PDF 文件')
        if value.size > 30 * 1024 * 1024:
            raise serializers.ValidationError('PDF 文件不能超过 30 MB')
        header = value.read(5)
        value.seek(0)
        if header != b'%PDF-':
            raise serializers.ValidationError('文件内容不是有效的 PDF')
        return value


class DocumentSearchSerializer(serializers.Serializer):
    """文档检索序列化器"""
    query = serializers.CharField(max_length=1000)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)