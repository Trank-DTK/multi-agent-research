# 文献助手的工具
from langchain_classic.tools import BaseTool
from documents.services import VectorService
from documents.models import Document
from typing import Optional,Any

class SearchLiteratureTool(BaseTool):
    """检索文献的工具"""
    name:str = "search_literature"
    description:str = "在已上传的文献库中检索相关内容。输入你的问题，工具会返回最相关的文献片段"

    user:Optional[Any] = None
    vector_service:Optional[VectorService] = None

    def __init__(self, user):
        super().__init__()
        self.user = user
        try:
            self.vector_service = VectorService()
            print(f"SearchLiteratureTool: VectorService 初始化成功")
        except Exception as e:
            print(f"SearchLiteratureTool: VectorService 初始化失败: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.vector_service = None

    def _run(self, query: str) -> str:
        try:
            if not self.vector_service:
                return "VectorService 未初始化，请检查日志"

            print(f"SearchLiteratureTool: 正在检索文献，查询: {query[:50]}")
            results = self.vector_service.search_similar(query, self.user, top_k=3)

            if not results:
                return "未找到相关文献内容"

            output = "找到以下相关内容：\n\n"
            for i, r in enumerate(results, 1):
                output += f"[{i}] 来自《{r['document_title']}》 (相似度: {r['score']:.2f})\n"
                output += f"{r['content'][:300]}...\n\n"

            print(f"SearchLiteratureTool: 检索成功，返回 {len(results)} 条结果")
            return output
        except Exception as e:
            print(f"SearchLiteratureTool._run() 错误: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"检索失败：{str(e)}"

    async def _arun(self, query: str) -> str:
        return await self._run(query)


class SummarizeDocumentTool(BaseTool):
    """总结文献的工具"""
    name:str = "summarize_document"
    description:str = "总结指定文献的内容。输入文献ID或标题"

    user:Optional[Any] = None

    def __init__(self, user):
        super().__init__()
        self.user = user
        print(f"SummarizeDocumentTool: 初始化成功，用户ID: {user.id}")

    def _run(self, query: str) -> str:
        try:
            print(f"SummarizeDocumentTool: 开始处理查询: {query[:50]}")

            # 尝试按ID查找
            if query.isdigit():
                print(f"SummarizeDocumentTool: 尝试按ID查找: {query}")
                doc = Document.objects.get(id=int(query), user=self.user)
            else:
                # 按标题模糊查找
                print(f"SummarizeDocumentTool: 尝试按标题查找: {query}")
                doc = Document.objects.filter(user=self.user, title__icontains=query).first()
                if not doc:
                    print(f"SummarizeDocumentTool: 未找到文献")
                    return f"未找到文献：{query}"

            print(f"SummarizeDocumentTool: 找到文献，标题: {doc.title}")

            # 获取所有分块内容
            chunks = doc.chunks.all().order_by('chunk_index')
            print(f"SummarizeDocumentTool: 找到 {chunks.count()} 个分块")

            full_text = "\n".join([c.content for c in chunks])

            # 简单总结（取前500字）
            summary = full_text[:500] + "..." if len(full_text) > 500 else full_text

            print(f"SummarizeDocumentTool: 处理成功，文本长度: {len(full_text)}")
            return f"文献《{doc.title}》摘要：\n{summary}"

        except Document.DoesNotExist:
            print(f"SummarizeDocumentTool: Document.DoesNotExist: {query}")
            return f"未找到文献：{query}"
        except Exception as e:
            print(f"SummarizeDocumentTool._run() 错误: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"总结失败：{str(e)}"

    async def _arun(self, query: str) -> str:
        return await self._run(query)