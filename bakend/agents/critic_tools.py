# 评审Agent工具
from langchain_classic.tools import BaseTool
from typing import Dict, Any, Optional
import json

class QualityEvaluatorTool(BaseTool):
    """质量评估工具"""
    name: str = "quality_evaluator"
    description: str = """评估研究内容的质量，返回评分和改进建议。
输入格式：需要评估的文本内容
输出：综合评分(1-10)、各维度评分、改进建议"""

    llm:Optional[Any] = None  
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, content: str) -> str:
        try:
            prompt = f"""请评估以下研究内容的质量，按照以下维度打分（1-10分）：

内容：
{content[:1500]}

评估维度：
1. 科学严谨性：逻辑是否严密，方法是否科学
2. 完整性：是否包含必要要素
3. 创新性：是否有新见解或新方法
4. 可操作性：是否具体可行
5. 表达清晰度：语言是否清晰，结构是否合理

请按以下格式输出：
【综合评分】X/10
【各维度评分】
- 科学严谨性：X/10
- 完整性：X/10
- 创新性：X/10
- 可操作性：X/10
- 表达清晰度：X/10
【改进建议】
1. ...
2. ...
【总体评价】一句话总结"""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "综合评分：?/10\n改进建议：需要LLM实例进行详细评估"
                
        except Exception as e:
            return f"质量评估失败：{str(e)}"
    
    async def _arun(self, content: str) -> str:
        return await self._run(content)


class ConsistencyCheckerTool(BaseTool):
    """一致性检查工具"""
    name: str = "consistency_checker"
    description: str = """检查研究内容之间的一致性，如文献调研与实验设计是否匹配。
输入格式：第一部分内容 | 第二部分内容
输出：一致性评分和矛盾点"""

    llm:Optional[Any] = None  
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, query: str) -> str:
        try:
            parts = query.split('|')
            if len(parts) < 2:
                return "输入格式错误，请使用 '内容1 | 内容2' 格式"
            
            content1 = parts[0][:800]
            content2 = parts[1][:800]
            
            prompt = f"""请检查以下两部分内容的一致性：

第一部分（文献调研/背景）：
{content1}

第二部分（实验设计/方案）：
{content2}

请分析：
1. 第二部分是否基于第一部分的发现？
2. 是否存在矛盾或冲突？
3. 是否有遗漏的关键点？

输出格式：
【一致性评分】X/10
【一致性分析】...
【矛盾点】（如有）
【建议调整】..."""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "一致性评分：?/10\n需要LLM实例进行详细检查"
                
        except Exception as e:
            return f"一致性检查失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return await self._run(query)


class FeasibilityCheckerTool(BaseTool):
    """可行性检查工具"""
    name: str = "feasibility_checker"
    description: str = """评估实验方案的可行性。
输入格式：实验设计方案
输出：可行性评分、资源需求、潜在风险"""

    llm:Optional[Any] = None  
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, content: str) -> str:
        try:
            prompt = f"""请评估以下实验方案的可行性：

实验方案：
{content[:1500]}

评估维度：
1. 技术可行性：现有技术是否能实现
2. 资源可行性：是否需要特殊设备/数据
3. 时间可行性：预计耗时是否合理
4. 成本可行性：预估成本是否可接受

输出格式：
【可行性评分】X/10
【技术可行性】...
【资源需求】...
【潜在风险】...
【优化建议】..."""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "可行性评分：?/10\n需要LLM实例进行详细评估"
                
        except Exception as e:
            return f"可行性检查失败：{str(e)}"
    
    async def _arun(self, content: str) -> str:
        return await self._run(content)


class NoveltyEvaluatorTool(BaseTool):
    """创新性评估工具"""
    name: str = "novelty_evaluator"
    description: str = """评估研究方案的新颖性和创新性。
输入格式：研究方案内容
输出：创新性评分、相似研究、创新点分析"""

    llm:Optional[Any] = None  
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, content: str) -> str:
        try:
            prompt = f"""请评估以下研究方案的创新性：

研究方案：
{content[:1500]}

评估要点：
1. 是否有新问题、新视角？
2. 是否提出新方法或改进？
3. 与现有研究相比有何不同？
4. 是否有潜在突破点？

输出格式：
【创新性评分】X/10
【创新点】...
【与现有研究的差异】...
【潜在突破价值】..."""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "创新性评分：?/10\n需要LLM实例进行详细评估"
                
        except Exception as e:
            return f"创新性评估失败：{str(e)}"
    
    async def _arun(self, content: str) -> str:
        return await self._run(content)