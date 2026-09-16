from django.conf import settings
from django.db import models


class ModelProvider(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="model_providers")
    name = models.CharField(max_length=100)
    protocol = models.CharField(max_length=20, choices=[("openai", "OpenAI compatible"), ("ollama", "Ollama")])
    base_url = models.URLField(max_length=500)
    model = models.CharField(max_length=200)
    encrypted_api_key = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name", "id"]
        constraints = [models.UniqueConstraint(fields=["user"], condition=models.Q(is_default=True), name="one_default_model_per_user")]
