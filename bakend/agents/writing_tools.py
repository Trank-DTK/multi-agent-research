# bakend/agents/writing_tools.py
from langchain_classic.tools import BaseTool
from typing import Optional
from langchain_community.llms import Ollama
from .agent import get_ollama_base_url
import re


class GenerateOutlineTool(BaseTool):
    """生成论文大纲的工具"""
    name: str = "generate_outline"
    description: str = "根据研究主题生成论文大纲。输入格式：主题:xxx 类型:research (类型可选：research/review/technical)"
    llm: Optional[object] = None
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.7
        )
    
    def _run(self, query: str) -> str:
        # 解析参数：主题:xxx 类型:xxx
        topic = query
        paper_type = "research"
        
        topic_match = re.search(r'主题[:：]\s*([^,，\s]+)', query)
        if topic_match:
            topic = topic_match.group(1)
        
        type_match = re.search(r'类型[:：]\s*(\w+)', query)
        if type_match:
            paper_type = type_match.group(1)
        
        prompt = f"""请为以下研究主题生成一份完整的论文大纲：

研究主题：{topic}
论文类型：{paper_type}

请按照标准学术论文结构生成大纲，包含以下部分（如果适用）：
1. 引言（Introduction）
2. 相关工作（Related Work）
3. 方法/理论（Methodology）
4. 实验/分析（Experiments/Analysis）
5. 结果与讨论（Results and Discussion）
6. 结论（Conclusion）

每个部分下可以包含子章节。请用Markdown格式输出。"""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class WriteSectionTool(BaseTool):
    """写作章节内容的工具"""
    name: str = "write_section"
    description: str = "根据大纲和上下文撰写论文章节内容。输入格式：标题:xxx 上下文:xxx 字数:500"
    llm: Optional[object] = None
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.8
        )
    
    def _run(self, query: str) -> str:
        # 解析参数
        section_title = query
        context = ""
        word_count = 500
        
        title_match = re.search(r'标题[:：]\s*([^,，]+)', query)
        if title_match:
            section_title = title_match.group(1).strip()
        
        context_match = re.search(r'上下文[:：]\s*(.+?)(?=字数[:：]|$)', query)
        if context_match:
            context = context_match.group(1).strip()
        
        word_match = re.search(r'字数[:：]\s*(\d+)', query)
        if word_match:
            word_count = int(word_match.group(1))
        
        prompt = f"""请撰写以下论文章节的内容：

章节标题：{section_title}

研究背景和上下文：
{context}

要求：
- 字数约{word_count}字
- 使用学术语言
- 逻辑清晰，层次分明
- 如有需要，可标注需要引用文献的位置（用[REF]标记）

请直接输出章节内容："""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class PolishTextTool(BaseTool):
    """学术润色工具"""
    name: str = "polish_text"
    description: str = "对文本进行学术润色。输入格式：文本:xxx 风格:academic (风格可选：academic/concise/formal)"
    llm: Optional[object] = None
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.5
        )
    
    def _run(self, query: str) -> str:
        # 解析参数
        text = query
        style = "academic"
        
        text_match = re.search(r'文本[:：]\s*(.+?)(?=风格[:：]|$)', query)
        if text_match:
            text = text_match.group(1).strip()
        
        style_match = re.search(r'风格[:：]\s*(\w+)', query)
        if style_match:
            style = style_match.group(1)
        
        prompt = f"""请对以下文本进行学术润色：

原文：
{text}

润色要求：
- 风格：{style}
- 改进语法和表达
- 使语言更加学术化、专业化
- 保持原意不变

请直接输出润色后的文本："""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class GenerateAbstractTool(BaseTool):
    """生成论文摘要的工具"""
    name: str = "generate_abstract"
    description: str = "根据论文内容生成摘要。输入格式：内容:xxx 字数限制:300"
    llm: Optional[object] = None
    max_input_chars: int = 15000  # 设置默认值
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.6
        )
    
    def _run(self, query: str) -> str:
        # 解析参数
        content = query
        word_limit = 300
        
        content_match = re.search(r'内容[:：]\s*(.+?)(?=字数限制[:：]|$)', query)
        if content_match:
            content = content_match.group(1).strip()
        
        limit_match = re.search(r'字数限制[:：]\s*(\d+)', query)
        if limit_match:
            word_limit = int(limit_match.group(1))

        truncated = content[:self.max_input_chars]
        
        prompt = f"""请根据以下论文内容生成摘要：

论文内容：
{truncated}

要求：
- 字数不超过{word_limit}字
- 包含：研究背景、目的、方法、结果、结论
- 语言简洁、信息完整

摘要："""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class AddCitationTool(BaseTool):
    """添加引用标记的工具"""
    name: str = "add_citation"
    description: str = "在文本中添加引用标记。输入格式：文本:xxx 引用信息:xxx"
    
    def _run(self, query: str) -> str:
        text = query
        citation_info = ""
        
        text_match = re.search(r'文本[:：]\s*(.+?)(?=引用信息[:：]|$)', query)
        if text_match:
            text = text_match.group(1).strip()
        
        citation_match = re.search(r'引用信息[:：]\s*(.+?)$', query)
        if citation_match:
            citation_info = citation_match.group(1).strip()
        
        return f"{text}\n\n[REF: {citation_info}]"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)