"""Join the extension setup and embedding history without changing user data."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0002_enable_pgvector"),
        ("documents", "0004_optional_embedding"),
    ]

    operations = []
