from django.urls import path, include
from accounts.provider_views import ProviderListView, ProviderDetailView, ProviderTestView
urlpatterns = [path('providers/', ProviderListView.as_view()), path('providers/<int:pk>/', ProviderDetailView.as_view()), path('providers/<int:pk>/test/', ProviderTestView.as_view()), path('', include('documents.urls'))]

from writing.section_views import SectionDetailView
urlpatterns += [path("papers/<int:paper_id>/sections/<int:section_id>/", SectionDetailView.as_view())]
