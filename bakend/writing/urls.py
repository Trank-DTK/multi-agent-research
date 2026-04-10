from django.urls import path
from .views import (
    GenerateOutlineView, PaperCreateView, PaperDetailView, PaperListView,
    PaperDeleteView, WriteSectionView, PolishTextView, GenerateAbstractView,
    ExportDocxView, WritingAgentChatView
)

urlpatterns = [
    path('outline/', GenerateOutlineView.as_view(), name='generate_outline'),
    path('papers/', PaperListView.as_view(), name='paper_list'),
    path('papers/create/', PaperCreateView.as_view(), name='paper_create'),
    path('papers/<int:paper_id>/', PaperDetailView.as_view(), name='paper_detail'),
    path('papers/<int:paper_id>/delete/', PaperDeleteView.as_view(), name='paper_delete'),
    path('papers/<int:paper_id>/section/', WriteSectionView.as_view(), name='write_section'),
    path('papers/<int:paper_id>/abstract/', GenerateAbstractView.as_view(), name='generate_abstract'),
    path('papers/<int:paper_id>/export/', ExportDocxView.as_view(), name='export_docx'),
    path('polish/', PolishTextView.as_view(), name='polish_text'),
    path('agent/', WritingAgentChatView.as_view(), name='writing_agent'),
]