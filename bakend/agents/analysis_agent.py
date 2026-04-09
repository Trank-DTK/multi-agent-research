# 数据分析Agent
# bakend/agents/analysis_agent.py
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.tools import BaseTool
import json
from .agent import get_ollama_base_url
from typing import Optional, Any

# 优先尝试导入OllamaLLM（langchain-ollama包），如果失败则回退到弃用的Ollama
try:
    from langchain_ollama import OllamaLLM
    LLM_CLASS = OllamaLLM
    USING_OLLAMA_LLM = True
    print("analysis_agent: 使用 langchain_ollama.OllamaLLM（推荐）")
except ImportError as e1:
    print(f"analysis_agent: 导入 OllamaLLM 失败: {e1}")
    try:
        from langchain_community.llms import Ollama
        LLM_CLASS = Ollama
        USING_OLLAMA_LLM = False
        print("analysis_agent: 使用 langchain_community.llms.Ollama（回退，已弃用）")
    except ImportError as e2:
        raise ImportError(f"无法导入OllamaLLM或Ollama: {e1}, {e2}")


class DataSummaryTool(BaseTool):
    """数据摘要工具"""
    name: str = "data_summary"
    description: str = "生成数据的摘要统计信息。输入数据描述，输出统计摘要"
    df: Optional[Any] = None
    
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
    df: Optional[Any] = None
    
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
        self._llm = llm

    def _run(self, query: str) -> str:
        if self._llm is None:
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

        try:
            # 尝试不同的调用方式
            try:
                # 尝试直接调用（Ollama）
                result = self._llm(prompt)
            except (AttributeError, TypeError):
                # 尝试invoke方法（OllamaLLM）
                result = self.llm.invoke(prompt)

            # 确保结果是字符串
            return str(result)
        except Exception as e:
            return f"生成洞察时出错: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


def create_analysis_agent(df=None, verbose=True):
    """创建数据分析Agent"""

    try:
        llm = LLM_CLASS(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.5
        )
        print(f"analysis_agent: LLM初始化成功，使用 {LLM_CLASS.__name__}")
    except Exception as e:
        print(f"analysis_agent: LLM初始化失败: {e}")
        raise

    tools = [
        DataSummaryTool(df=df),
        CorrelationAnalysisTool(df=df),
        InsightGeneratorTool(llm=llm),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 如果提供了数据，将数据概览添加到内存中，让Agent知道数据内容
    if df is not None:
        try:
            # 生成数据概览
            row_count = len(df)
            col_count = len(df.columns)
            columns_preview = ', '.join(df.columns[:10])  # 最多显示10个列名
            if len(df.columns) > 10:
                columns_preview += f' ... 等共{col_count}列'

            # 添加系统消息，描述数据集
            system_message = f"""你是一个数据分析助手。用户上传了一个数据集，包含{row_count}行{col_count}列数据。

列名：{columns_preview}

你可以使用以下工具分析数据：
1. data_summary: 生成数据摘要统计信息
2. correlation_analysis: 分析数值列之间的相关性
3. insight_generator: 根据分析结果生成业务洞察

当用户询问数据内容时，你可以使用data_summary工具查看数据概览。"""

            # 将系统消息添加到内存中作为AI消息
            memory.chat_memory.add_ai_message(system_message)

            # 生成更详细的数据摘要并添加到内存，让Agent直接知道数据内容
            try:
                # 获取数据类型信息
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

                # 生成摘要文本
                summary_lines = []
                summary_lines.append(f"数据集详细摘要:")
                summary_lines.append(f"- 总行数: {row_count}")
                summary_lines.append(f"- 总列数: {col_count}")
                summary_lines.append(f"- 数值列 ({len(numeric_cols)}): {', '.join(numeric_cols[:5])}" +
                                    (f" ..." if len(numeric_cols) > 5 else ""))
                summary_lines.append(f"- 文本/分类列 ({len(categorical_cols)}): {', '.join(categorical_cols[:5])}" +
                                    (f" ..." if len(categorical_cols) > 5 else ""))
                if datetime_cols:
                    summary_lines.append(f"- 日期时间列 ({len(datetime_cols)}): {', '.join(datetime_cols)}")

                # 添加缺失值信息
                missing_counts = df.isnull().sum()
                total_missing = missing_counts.sum()
                if total_missing > 0:
                    summary_lines.append(f"- 缺失值总数: {total_missing}")
                    cols_with_missing = missing_counts[missing_counts > 0].index.tolist()
                    summary_lines.append(f"- 有缺失值的列: {', '.join(cols_with_missing[:5])}" +
                                        (f" ..." if len(cols_with_missing) > 5 else ""))

                summary_text = '\n'.join(summary_lines)
                memory.chat_memory.add_ai_message(summary_text)
                print(f"analysis_agent: 已添加数据概览和详细摘要到内存，{row_count}行{col_count}列")
            except Exception as summary_error:
                print(f"analysis_agent: 生成详细摘要时出错: {summary_error}")
                # 如果生成详细摘要失败，至少添加一个简单摘要
                simple_summary = f"数据集包含{row_count}行{col_count}列数据。列名: {columns_preview}"
                memory.chat_memory.add_ai_message(simple_summary)
        except Exception as e:
            print(f"analysis_agent: 添加数据概览到内存时出错: {e}")
            import traceback
            traceback.print_exc()

    try:
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=verbose,
            handle_parsing_errors=True
        )
        print("analysis_agent: Agent创建成功")
        return agent
    except Exception as e:
        print(f"analysis_agent: Agent创建失败: {e}")
        import traceback
        traceback.print_exc()
        raise