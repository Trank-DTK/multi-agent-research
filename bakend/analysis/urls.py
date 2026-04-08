from django.urls import path
from .views import (
    DatasetUploadView, DatasetListView, DatasetDetailView, DatasetDeleteView,
    DataAnalysisView, DataVisualizationView
)

urlpatterns = [
    path('datasets/upload/', DatasetUploadView.as_view(), name='dataset_upload'),
    path('datasets/', DatasetListView.as_view(), name='dataset_list'),
    path('datasets/<int:dataset_id>/', DatasetDetailView.as_view(), name='dataset_detail'),
    path('datasets/<int:dataset_id>/delete/', DatasetDeleteView.as_view(), name='dataset_delete'),
    path('datasets/<int:dataset_id>/analyze/', DataAnalysisView.as_view(), name='data_analysis'),
    path('datasets/<int:dataset_id>/visualize/', DataVisualizationView.as_view(), name='data_visualize'),
]