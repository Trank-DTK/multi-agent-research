from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Section
        fields=['id','title','content']
        read_only_fields=['id']
class SectionDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self, request, paper_id, section_id):
        section=get_object_or_404(Section,pk=section_id,paper_id=paper_id,paper__user=request.user)
        serializer=SectionSerializer(section,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        section.paper.save()
        return Response(serializer.data)
    def delete(self, request, paper_id, section_id):
        section=get_object_or_404(Section,pk=section_id,paper_id=paper_id,paper__user=request.user)
        paper=section.paper
        section.delete()
        paper.save()
        return Response(status=204)
