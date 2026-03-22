# 文献助手的工具
from langchain_classic.tools import BaseTool
from documents.services import VectorService
from documents.models import Document

class SearchLiteratureTool(BaseTool):
    """检索文献的工具"""
    name = "search_literature"
    description = "在已上传的文献库中检索相关内容。输入你的问题，工具会返回最相关的文献片段"
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.vector_service = VectorService()
    
    def _run(self, query: str) -> str:
        try:
            results = self.vector_service.search_similar(query, self.user, top_k=3)
            
            if not results:
                return "未找到相关文献内容"
            
            output = "找到以下相关内容：\n\n"
            for i, r in enumerate(results, 1):
                output += f"[{i}] 来自《{r['document_title']}》 (相似度: {r['score']:.2f})\n"
                output += f"{r['content'][:300]}...\n\n"
            
            return output
        except Exception as e:
            return f"检索失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class SummarizeDocumentTool(BaseTool):
    """总结文献的工具"""
    name = "summarize_document"
    description = "总结指定文献的内容。输入文献ID或标题"
    
    def __init__(self, user):
        super().__init__()
        self.user = user
    
    def _run(self, query: str) -> str:
        try:
            # 尝试按ID查找
            if query.isdigit():
                doc = Document.objects.get(id=int(query), user=self.user)
            else:
                # 按标题模糊查找
                doc = Document.objects.filter(user=self.user, title__icontains=query).first()
                if not doc:
                    return f"未找到文献：{query}"
            
            # 获取所有分块内容
            chunks = doc.chunks.all().order_by('chunk_index')
            full_text = "\n".join([c.content for c in chunks])
            
            # 简单总结（取前500字）
            summary = full_text[:500] + "..." if len(full_text) > 500 else full_text
            
            return f"文献《{doc.title}》摘要：\n{summary}"
            
        except Document.DoesNotExist:
            return f"未找到文献：{query}"
        except Exception as e:
            return f"总结失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)