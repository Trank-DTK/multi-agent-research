from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField
import os

class Document(models.Model):
    """上传的文献文档"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=500, verbose_name='标题')
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name='PDF文件')
    file_name = models.CharField(max_length=500, verbose_name='原始文件名')
    file_size = models.IntegerField(verbose_name='文件大小(字节)', default=0)
    page_count = models.IntegerField(verbose_name='页数', default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = '文档'
        verbose_name_plural = '文档'
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        """删除时同时删除文件"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class DocumentChunk(models.Model):
    """文档分块（用于向量检索）"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField(verbose_name='分块序号')
    content = models.TextField(verbose_name='文本内容')
    embedding = VectorField(dimensions=1536, verbose_name='向量')  # qwen2.5的向量维度
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        verbose_name = '文档分块'
        verbose_name_plural = '文档分块'
    
    def __str__(self):
        return f"{self.document.title} - 块{self.chunk_index}"