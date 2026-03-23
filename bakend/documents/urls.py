from django.urls import path
from .views import DocumentUploadView, DocumentListView, DocumentDeleteView, DocumentSearchView

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/<int:doc_id>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    path('documents/search/', DocumentSearchView.as_view(), name='document_search'),
]