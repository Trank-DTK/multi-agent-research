# 序列化器
from rest_framework import serializers
from .models import Dataset, AnalysisResult, DataVisualization

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'description', 'file_name', 'file_size', 
                  'row_count', 'column_count', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class DatasetUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField()


class AnalysisRequestSerializer(serializers.Serializer):
    analysis_type = serializers.CharField()  # descriptive, correlation, summary
    columns = serializers.ListField(child=serializers.CharField(), required=False)


class VisualizationRequestSerializer(serializers.Serializer):
    chart_type = serializers.CharField()
    x_column = serializers.CharField()
    y_column = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)