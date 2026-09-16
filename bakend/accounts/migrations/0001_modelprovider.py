from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="ModelProvider", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("name", models.CharField(max_length=100)),
        ("protocol", models.CharField(choices=[("openai", "OpenAI compatible"), ("ollama", "Ollama")], max_length=20)),
        ("base_url", models.URLField(max_length=500)),
        ("model", models.CharField(max_length=200)),
        ("encrypted_api_key", models.TextField(blank=True)),
        ("is_default", models.BooleanField(default=False)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="model_providers", to=settings.AUTH_USER_MODEL)),
    ], options={"ordering": ["-is_default", "name", "id"], "constraints": [models.UniqueConstraint(fields=("user",), condition=models.Q(is_default=True), name="one_default_model_per_user")]})]
