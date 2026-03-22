# RAG
import os
import PyPDF2
from django.core.files.storage import default_storage
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .models import Document, DocumentChunk
from agents.agent import get_ollama_base_url

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
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks


class VectorService:
    """向量服务"""
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url()
        )
    
    def generate_embedding(self, text):
        """生成文本向量"""
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
    
    def search_similar(self, query, user, top_k=5):
        """检索相似文档块"""
        query_vector = self.generate_embedding(query)
        
        # 使用pgvector的余弦相似度检索
        from pgvector.django import CosineDistance
        
        chunks = DocumentChunk.objects.filter(
            document__user=user  #只检索当前用户的文献
        ).annotate(
            distance=CosineDistance('embedding', query_vector)
        ).order_by('distance')[:top_k]   #按距离排序，取前top_k个
        
        results = []
        for chunk in chunks:
            results.append({
                'document_id': chunk.document.id,
                'document_title': chunk.document.title,
                'content': chunk.content,
                'score': 1 - chunk.distance  # 距离越小相似度越高，转换后score越高越相关
            })
        
        return results