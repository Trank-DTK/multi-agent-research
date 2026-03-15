from rest_framework import serializers

class ChatMessageSerializer(serializers.Serializer):
    """聊天请求序列化器"""
    sender = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """聊天响应序列化器"""
    response = serializers.CharField(help_text="AI的回复")
    model = serializers.CharField(default="qwen2.5-7b",help_text="使用的模型")
