from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ModelProvider
from .provider_service import encrypt_key, validate_base_url, build_llm


class ProviderSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=4096, trim_whitespace=True)
    has_api_key = serializers.SerializerMethodField()
    class Meta:
        model = ModelProvider
        fields = ["id", "name", "protocol", "base_url", "model", "is_default", "api_key", "has_api_key"]
        read_only_fields = ["id", "has_api_key"]
    def get_has_api_key(self, obj):
        return bool(obj.encrypted_api_key)
    def validate_base_url(self, value):
        try:
            return validate_base_url(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
    def validate(self, attrs):
        if self.instance and "api_key" not in attrs and any(attrs.get(field, getattr(self.instance, field)) != getattr(self.instance, field) for field in ("base_url", "protocol")) and self.instance.encrypted_api_key:
            raise serializers.ValidationError({"api_key": "修改地址或协议时请重新填写密钥，或勾选清除密钥"})
        return attrs
    def create(self, data):
        data["encrypted_api_key"] = encrypt_key(data.pop("api_key", ""))
        return super().create(data)
    def update(self, instance, data):
        if "api_key" in data:
            data["encrypted_api_key"] = encrypt_key(data.pop("api_key"))
        return super().update(instance, data)


class ProviderListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProviderSerializer
    def get_queryset(self):
        return ModelProvider.objects.filter(user=self.request.user)
    @transaction.atomic
    def perform_create(self, serializer):
        get_user_model().objects.select_for_update().get(pk=self.request.user.pk)
        make_default = serializer.validated_data.get("is_default", False) or not self.get_queryset().exists()
        if make_default:
            self.get_queryset().update(is_default=False)
        serializer.save(user=self.request.user, is_default=make_default)


class ProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProviderSerializer
    def get_queryset(self):
        return ModelProvider.objects.filter(user=self.request.user)
    @transaction.atomic
    def perform_update(self, serializer):
        get_user_model().objects.select_for_update().get(pk=self.request.user.pk)
        if serializer.validated_data.get("is_default"):
            self.get_queryset().exclude(pk=serializer.instance.pk).update(is_default=False)
        serializer.save()
    @transaction.atomic
    def perform_destroy(self, instance):
        get_user_model().objects.select_for_update().get(pk=self.request.user.pk)
        was_default = instance.is_default
        instance.delete()
        if was_default:
            other = self.get_queryset().first()
            if other:
                other.is_default = True
                other.save()


class ProviderTestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        provider = get_object_or_404(ModelProvider, pk=pk, user=request.user)
        try:
            build_llm(provider=provider).chat([{"role": "user", "content": "Reply with OK."}], timeout=30)
            return Response({"message": "连接成功，模型已返回文本"})
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
