from django.db import migrations
import pgvector.django
class Migration(migrations.Migration):
    dependencies = [("documents", "0003_documentchunk_idx_chunk_document_and_more")]
    operations = [migrations.AlterField(model_name="documentchunk", name="embedding", field=pgvector.django.VectorField(dimensions=3072, null=True, blank=True, verbose_name="向量"))]
