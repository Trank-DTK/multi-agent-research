# 实验助手工具
from langchain_classic.tools import BaseTool
from datetime import datetime
import json

class DesignExperimentTool(BaseTool):
    """设计实验方案的工具"""
    name = "design_experiment"
    description = """根据研究问题和相关文献，设计实验方案。
输入格式：研究问题描述，可包含关键词。
输出包含：实验目标、假设、实验步骤、所需材料、预期结果。"""
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, query: str) -> str:
        try:
            prompt = f"""你是一位实验设计专家。请根据以下研究问题，设计一个完整的实验方案：

研究问题：{query}

请按以下格式输出：
【实验目标】明确说明实验要验证什么
【研究假设】提出可验证的假设
【实验步骤】详细列出步骤（1. 2. 3. ...）
【所需材料】列出需要的设备、试剂、数据等
【预期结果】预测可能的结果
【注意事项】需要注意的问题

请确保方案科学、可行。"""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "需要提供LLM实例才能设计实验方案"
                
        except Exception as e:
            return f"实验设计失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class ValidateHypothesisTool(BaseTool):
    """验证假设的工具"""
    name = "validate_hypothesis"
    description = """根据文献证据验证研究假设。
输入格式：假设陈述
输出：基于文献的支持/反对证据"""
    
    def __init__(self, user, vector_service=None):
        super().__init__()
        self.user = user
        self.vector_service = vector_service
    
    def _run(self, query: str) -> str:
        try:
            # 在已上传文献中检索相关证据
            if self.vector_service:
                results = self.vector_service.search_similar(query, self.user, top_k=3)
                
                if not results:
                    return "未找到相关文献支持或反驳该假设"
                
                evidence = []
                for r in results:
                    evidence.append(f"来自《{r['document_title']}》 (相关度: {r['score']:.2f}):\n{r['content'][:200]}...")
                
                return f"文献证据：\n\n" + "\n\n".join(evidence)
            else:
                return "需要向量检索服务才能验证假设"
                
        except Exception as e:
            return f"假设验证失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class GenerateMethodologyTool(BaseTool):
    """生成研究方法论的工具"""
    name = "generate_methodology"
    description = """根据研究领域生成研究方法论建议。
输入格式：研究领域（如：机器学习、生物信息学、材料科学）
输出：推荐的研究方法、分析技术、工具等"""
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, query: str) -> str:
        try:
            prompt = f"""请为以下研究领域推荐研究方法论：

研究领域：{query}

请包括：
1. 主流研究方法（定性/定量）
2. 数据收集方法
3. 数据分析技术
4. 常用工具和软件
5. 最佳实践建议"""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return f"需要LLM实例才能生成方法论\n\n推荐的通用方法：\n- 文献综述\n- 实验设计\n- 数据统计分析"
                
        except Exception as e:
            return f"方法论生成失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class LiteratureToExperimentTool(BaseTool):
    """将文献发现转化为实验建议的工具"""
    name = "literature_to_experiment"
    description = """基于文献检索结果，生成实验建议。
输入格式：文献摘要或研究问题
输出：可操作的实验建议"""
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, query: str) -> str:
        try:
            prompt = f"""请根据以下文献信息或研究问题，提出具体的实验建议：

输入：{query}

请输出：
1. 可以验证的研究方向
2. 具体的实验设计建议
3. 可能遇到的挑战
4. 成功的判断标准"""
            
            if self.llm:
                response = self.llm.invoke(prompt)
                return response
            else:
                return "基于文献的实验建议：\n1. 重复验证文献中的核心发现\n2. 尝试新的变量组合\n3. 在不同条件下测试"
                
        except Exception as e:
            return f"实验建议生成失败：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)