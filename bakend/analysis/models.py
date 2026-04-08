# 数据模型
from django.db import models
from django.contrib.auth.models import User
import os

class Dataset(models.Model):
    """数据集模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=200, verbose_name='数据集名称')
    description = models.TextField(blank=True, verbose_name='描述')
    file = models.FileField(upload_to='datasets/%Y/%m/', verbose_name='数据文件')
    file_name = models.CharField(max_length=500, verbose_name='原始文件名')
    file_size = models.IntegerField(verbose_name='文件大小(字节)', default=0)
    row_count = models.IntegerField(verbose_name='行数', default=0)
    column_count = models.IntegerField(verbose_name='列数', default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = '数据集'
        verbose_name_plural = '数据集'
    
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class AnalysisResult(models.Model):
    """分析结果模型"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='results')
    analysis_type = models.CharField(max_length=50, verbose_name='分析类型')
    result_data = models.JSONField(default=dict, verbose_name='结果数据')
    chart_data = models.JSONField(default=dict, verbose_name='图表数据')
    insight = models.TextField(blank=True, verbose_name='AI洞察')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class DataVisualization(models.Model):
    """数据可视化模型"""
    CHART_TYPES = [
        ('line', '折线图'),
        ('bar', '柱状图'),
        ('scatter', '散点图'),
        ('histogram', '直方图'),
        ('box', '箱线图'),
    ]
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='visualizations')
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    x_column = models.CharField(max_length=100)
    y_column = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, blank=True)
    chart_config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
