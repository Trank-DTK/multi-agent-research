# 引用管理
import re
from .models import Citation

class CitationService:
    """引用管理服务"""
    
    @staticmethod
    def extract_citations(text: str) -> list:
        """提取文本中的引用标记"""
        pattern = r'\[REF:[^\]]+\]'
        return re.findall(pattern, text)
    
    @staticmethod
    def format_bibtex(citation: dict) -> str:
        """生成BibTeX格式"""
        return f"""@article{{{citation.get('key', 'ref')},
  author = {{{citation.get('authors', '')}}},
  title = {{{citation.get('title', '')}}},
  journal = {{{citation.get('journal', '')}}},
  year = {{{citation.get('year', '')}}},
  doi = {{{citation.get('doi', '')}}}
}}"""