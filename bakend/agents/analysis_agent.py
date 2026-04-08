# 数据分析Agent
# bakend/agents/analysis_agent.py
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.tools import BaseTool
from langchain_community.llms import Ollama
import json
from .agent import get_ollama_base_url


class DataSummaryTool(BaseTool):
    """数据摘要工具"""
    name: str = "data_summary"
    description: str = "生成数据的摘要统计信息。输入数据描述，输出统计摘要"
    
    def __init__(self, df=None):
        super().__init__()
        self.df = df
    
    def _run(self, query: str) -> str:
        if self.df is None:
            return "未加载数据"
        
        summary = f"""
数据概览：
- 行数：{len(self.df)}
- 列数：{len(self.df.columns)}
- 列名：{', '.join(self.df.columns[:10])}

数值列统计：
{self.df.describe().to_string()}

缺失值情况：
{self.df.isnull().sum().to_string()}
"""
        return summary
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class CorrelationAnalysisTool(BaseTool):
    """相关性分析工具"""
    name: str = "correlation_analysis"
    description: str = "分析数值列之间的相关性。输入列名（可选），输出相关系数矩阵"
    
    def __init__(self, df=None):
        super().__init__()
        self.df = df
    
    def _run(self, query: str) -> str:
        if self.df is None:
            return "未加载数据"
        
        import numpy as np
        numeric_df = self.df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return "没有数值列可用于相关性分析"
        
        # 计算相关系数矩阵
        corr = numeric_df.corr()
        
        # 找出最强相关性
        strong_pairs = []
        for i, col1 in enumerate(numeric_df.columns):
            for j, col2 in enumerate(numeric_df.columns):
                if i < j:
                    val = corr.loc[col1, col2]
                    if abs(val) > 0.7:
                        strong_pairs.append(f"{col1} 与 {col2}: {val:.3f}")
        
        result = f"相关系数矩阵（前5列）：\n{corr.iloc[:5, :5].to_string()}\n\n"
        if strong_pairs:
            result += f"强相关对（|r|>0.7）：\n" + "\n".join(strong_pairs)
        else:
            result += "未发现强相关关系"
        
        return result
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class InsightGeneratorTool(BaseTool):
    """洞察生成工具"""
    name: str = "insight_generator"
    description: str = "根据数据分析结果生成业务洞察和建议"
    
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
    
    def _run(self, query: str) -> str:
        if self.llm is None:
            return "需要LLM实例生成洞察"
        
        prompt = f"""请根据以下数据分析结果，生成3-5条关键洞察和建议：

{query}

输出格式：
【关键发现】
1. ...
2. ...

【建议】
1. ...
2. ..."""
        
        return self.llm.invoke(prompt)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


def create_analysis_agent(df=None, verbose=True):
    """创建数据分析Agent"""
    
    llm = Ollama(
        model="qwen2.5:7b",
        base_url=get_ollama_base_url(),
        temperature=0.5
    )
    
    tools = [
        DataSummaryTool(df=df),
        CorrelationAnalysisTool(df=df),
        InsightGeneratorTool(llm=llm),
    ]
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    return agent