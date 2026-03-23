"""
文献检索功能诊断脚本
运行方式: docker exec -it research_web python manage.py shell < debug_literature.py
"""
import os
import sys
import django

# 设置 Django 环境
import os
import sys

# 兼容 Docker 和本地运行环境
if os.path.exists('/app'):
    # Docker 环境
    sys.path.insert(0, '/app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakend.settings')
else:
    # 本地环境 - 临时使用 SQLite
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(script_dir)  # bakend/
    backend_root = os.path.join(current_dir, 'bakend')  # bakend/bakend/
    sys.path.insert(0, backend_root)
    sys.path.insert(0, current_dir)  # 应用目录优先级更高
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakend.settings')

# 临时修改数据库配置为 SQLite
from pathlib import Path
import django.conf
django.conf.settings.DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(backend_root).parent / 'db.sqlite3',
    }
}

django.setup()

from documents.models import Document, DocumentChunk
from documents.services import VectorService

def check_documents():
    """检查文档数量"""
    print("=" * 50)
    print("1. 检查数据库中的文档")
    print("=" * 50)

    documents = Document.objects.all()
    print(f"总文档数: {documents.count()}")

    for doc in documents:
        chunks_count = doc.chunks.count()
        print(f"\n文档: {doc.title}")
        print(f"  ID: {doc.id}")
        print(f"  分块数: {chunks_count}")

        if chunks_count > 0:
            # 显示第一个分块
            first_chunk = doc.chunks.first()
            print(f"  第一个分块内容: {first_chunk.content[:100]}...")
            print(f"  向量维度: {len(first_chunk.embedding) if hasattr(first_chunk, 'embedding') and first_chunk.embedding is not None else 'None'}")
            print(f"  向量是否为numpy数组: {type(first_chunk.embedding).__name__ if hasattr(first_chunk, 'embedding') else 'N/A'}")

    print("\n")

def check_vector_service():
    """检查向量服务"""
    print("=" * 50)
    print("2. 测试向量服务")
    print("=" * 50)

    vector_service = VectorService()

    # 测试文本
    test_text = "机器学习是人工智能的一个分支"
    print(f"测试文本: {test_text}")

    # 生成向量
    try:
        embedding = vector_service.generate_embedding(test_text)
        print(f"[OK] 向量生成成功")
        print(f"  向量维度: {len(embedding)}")
        print(f"  向量范围: [{min(embedding):.4f}, {max(embedding):.4f}]")
    except Exception as e:
        print(f"[ERROR] 向量生成失败: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n")

def test_search():
    """测试检索功能"""
    print("=" * 50)
    print("3. 测试检索功能")
    print("=" * 50)

    # 获取第一个用户
    users = Document.objects.values_list('user__id', flat=True).distinct()
    if not users:
        print("数据库中没有用户")
        return

    test_user_id = users[0]
    print(f"测试用户 ID: {test_user_id}")

    vector_service = VectorService()
    query = "人工智能"

    print(f"查询: {query}")

    try:
        results = vector_service.search_similar(query, test_user_id, top_k=3)
        print(f"\n✓ 检索成功")
        print(f"  返回结果数: {len(results)}")

        if results:
            for i, r in enumerate(results, 1):
                print(f"\n  结果 {i}:")
                print(f"    文档: {r['document_title']}")
                print(f"    相似度: {r['score']:.4f}")
                print(f"    内容: {r['content'][:100]}...")
        else:
            print("  (未找到匹配结果)")
    except Exception as e:
        print(f"[ERROR] 检索失败: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n")

def main():
    """主函数"""
    print("\n文献检索功能诊断工具\n")

    check_documents()
    check_vector_service()
    test_search()

    print("=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
