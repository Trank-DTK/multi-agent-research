"""
自动启用 pgvector 扩展。

为什么需要这个迁移：
    `ankane/pgvector` 镜像虽然自带了 pgvector 扩展的二进制文件，但 PostgreSQL
    的扩展必须【在每个数据库里 CREATE EXTENSION 一次】才会生效。
    如果忘了这一步，任何带 `vector(N)` 字段的迁移都会报：

        django.db.utils.ProgrammingError: type "vector" does not exist

    本迁移依赖 0001_initial，用于已有数据库补齐扩展启用记录；
    它不能在 0001_initial 创建 vector 字段之前执行。全新 PostgreSQL
    数据库仍需预先启用扩展。0005_merge_pgvector 将本分支与字段迁移合并。

    CREATE EXTENSION IF NOT EXISTS 是幂等的，重复执行不会有副作用。

注意：本迁移只跑一句 SQL，不涉及模型字段变更，所以用 RunPython 即可；
      回滚时不做任何事（扩展留着无害）。
"""

from django.db import migrations


def enable_pgvector(apps, schema_editor):
    """在 PostgreSQL 上启用 vector 扩展；其他数据库（如测试用的 SQLite）自动跳过。"""
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def noop(apps, schema_editor):
    """回滚时什么都不做：删掉扩展可能影响其他数据，留着无害。"""
    return


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_pgvector, noop),
    ]
