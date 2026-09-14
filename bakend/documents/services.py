# RAG
import os
import PyPDF2
from django.core.files.storage import default_storage
from .models import Document, DocumentChunk

class PDFParseService:
    """PDF解析服务"""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """从PDF提取文本"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text, len(pdf_reader.pages)
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")
    
    @staticmethod
    def split_text(text, chunk_size=500, chunk_overlap=50):
        """文本分块"""
        if chunk_size <= chunk_overlap or chunk_overlap < 0:
            raise ValueError('分块长度必须大于重叠长度')
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = max(text.rfind('\n', start + chunk_size // 2, end), text.rfind('。', start + chunk_size // 2, end))
                if boundary > start:
                    end = boundary + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == len(text):
                break
            start = max(start + 1, end - chunk_overlap)
        return chunks



class VectorService:
    """向量服务"""
    
    def __init__(self):
        self.embeddings = None

    def generate_embedding(self, text):
        from langchain_ollama import OllamaEmbeddings
        if self.embeddings is None:
            self.embeddings = OllamaEmbeddings(model=os.environ.get('EMBEDDING_MODEL', 'qwen2.5:7b'), base_url=os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'))
        return self.embeddings.embed_query(text)

    def create_chunks_with_vectors(self, document, chunks):
        """创建分块并生成向量"""
        for idx, chunk_text in enumerate(chunks):
            try:
                vector = self.generate_embedding(chunk_text) #生成向量
                DocumentChunk.objects.create(    
                    document=document,
                    chunk_index=idx,
                    content=chunk_text,
                    embedding=vector
                )
            except Exception as e:
                print(f"生成向量失败 (块{idx}): {str(e)}")
                continue
    
    def search_similar(self, query, user, top_k=5, document_ids=None):
        import re
        import heapq
        chunks = DocumentChunk.objects.filter(document__user=user).select_related('document')
        if document_ids is not None:
            chunks = chunks.filter(document_id__in=document_ids)
        words = re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]', query.lower())
        han = ''.join(re.findall(r'[\u4e00-\u9fff]', query))
        words += [han[i:i+2] for i in range(max(0, len(han)-1))]
        words = set(words)
        def rank(chunk):
            text = (chunk.document.title + ' ' + chunk.content).lower()
            return sum(1 for word in words if word in text) / max(1, len(words))
        ranked = heapq.nlargest(top_k, ((rank(c), c.pk, c) for c in chunks.iterator()), key=lambda item: (item[0], -item[1]))
        return [{'document_id': c.document_id, 'document_title': c.document.title, 'content': c.content, 'score': score} for score, _, c in ranked if score > 0]
