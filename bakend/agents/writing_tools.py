# 论文写作工具
from langchain_classic.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_community.llms import Ollama
from .agent import get_ollama_base_url


class GenerateOutlineInput(BaseModel):
    """生成论文大纲的输入参数"""
    topic: str = Field(description="论文主题或研究问题")
    paper_type: str = Field(default="research", description="论文类型：research/review/technical")


class GenerateOutlineTool(BaseTool):
    """生成论文大纲的工具"""
    name: str = "generate_outline"
    description: str = "根据研究主题生成论文大纲（章节结构）"
    args_schema: Type[BaseModel] = GenerateOutlineInput
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.7
        )
    
    def _run(self, topic: str, paper_type: str = "research") -> str:
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
    
    async def _arun(self, topic: str, paper_type: str = "research") -> str:
        return self._run(topic, paper_type)


class WriteSectionInput(BaseModel):
    """写作章节的输入参数"""
    section_title: str = Field(description="章节标题")
    context: str = Field(description="上下文信息（研究问题、大纲等）")
    word_count: Optional[int] = Field(default=500, description="目标字数")


class WriteSectionTool(BaseTool):
    """写作章节内容的工具"""
    name: str = "write_section"
    description: str = "根据大纲和上下文撰写论文章节内容"
    args_schema: Type[BaseModel] = WriteSectionInput
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.8
        )
    
    def _run(self, section_title: str, context: str, word_count: int = 500) -> str:
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
    
    async def _arun(self, section_title: str, context: str, word_count: int = 500) -> str:
        return self._run(section_title, context, word_count)


class PolishTextInput(BaseModel):
    """润色文本的输入参数"""
    text: str = Field(description="需要润色的文本")
    style: str = Field(default="academic", description="风格：academic/concise/formal")


class PolishTextTool(BaseTool):
    """学术润色工具"""
    name: str = "polish_text"
    description: str = "对文本进行学术润色，改进语言表达"
    args_schema: Type[BaseModel] = PolishTextInput
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.5
        )
    
    def _run(self, text: str, style: str = "academic") -> str:
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
    
    async def _arun(self, text: str, style: str = "academic") -> str:
        return self._run(text, style)


class GenerateAbstractInput(BaseModel):
    """生成摘要的输入参数"""
    paper_content: str = Field(description="论文完整内容或主要内容摘要")
    word_limit: Optional[int] = Field(default=300, description="字数限制")


class GenerateAbstractTool(BaseTool):
    """生成论文摘要的工具"""
    name: str = "generate_abstract"
    description: str = "根据论文内容生成摘要"
    args_schema: Type[BaseModel] = GenerateAbstractInput
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm or Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.6
        )
    
    def _run(self, paper_content: str, word_limit: int = 300) -> str:
        # 截取足够的内容（但不要超过上下文窗口）
        truncated = paper_content[:self.max_input_chars]
        
        prompt = f"""请根据以下论文内容生成摘要：

论文内容：
{truncated}

要求：
- 字数不超过{word_limit}字
- 包含：研究背景、目的、方法、结果、结论
- 语言简洁、信息完整

摘要："""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, paper_content: str, word_limit: int = 300) -> str:
        return self._run(paper_content, word_limit)


class AddCitationInput(BaseModel):
    """添加引用的输入参数"""
    text: str = Field(description="需要添加引用的文本")
    citation_info: str = Field(description="引用信息（作者、年份等）")


class AddCitationTool(BaseTool):
    """添加引用标记的工具"""
    name: str = "add_citation"
    description: str = "在文本中合适的位置添加引用标记"
    args_schema: Type[BaseModel] = AddCitationInput
    
    def _run(self, text: str, citation_info: str) -> str:
        # 在文本中适当位置插入引用标记
        prompt = f"""请在以下文本中适当的位置插入引用标记。

文本：
{text}

需要引用的信息：
{citation_info}

要求：
- 在引用点插入 [REF: {citation_info[:50]}]
- 保持文本流畅

输出修改后的文本："""
        
        # 简单实现：在末尾添加引用
        return f"{text}\n\n[REF: {citation_info}]"
    
    async def _arun(self, text: str, citation_info: str) -> str:
        return self._run(text, citation_info)