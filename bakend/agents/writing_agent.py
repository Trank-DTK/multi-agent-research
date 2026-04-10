# 写作助手
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from .writing_tools import (
    GenerateOutlineTool, WriteSectionTool, 
    PolishTextTool, GenerateAbstractTool, AddCitationTool
)
from .agent import get_ollama_base_url


def create_writing_agent(verbose=True):
    """创建论文写作Agent"""
    
    llm = Ollama(
        model="qwen2.5:7b",
        base_url=get_ollama_base_url(),
        temperature=0.7
    )
    
    tools = [
        GenerateOutlineTool(llm=llm),
        WriteSectionTool(llm=llm),
        PolishTextTool(llm=llm),
        GenerateAbstractTool(llm=llm),
        AddCitationTool(),
    ]
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    return agent


class WritingService:
    """论文写作服务"""

    def __init__(self):
        self.agent = create_writing_agent(verbose=False)
        # 创建独立的工具实例，避免agent路由错误
        self.llm = Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.5
        )
        self.polish_tool = PolishTextTool(llm=self.llm)
    
    def generate_outline(self, topic: str, paper_type: str = "research") -> str:
        """生成论文大纲"""
        return self.agent.run(f"使用generate_outline工具生成大纲，主题：{topic}，类型：{paper_type}")
    
    def write_section(self, section_title: str, context: str, word_count: int = 500) -> str:
        """撰写章节"""
        return self.agent.run(
            f"使用write_section工具撰写章节'{section_title}'，"
            f"上下文：{context}，目标字数：{word_count}"
        )
    
    def polish_text(self, text: str, style: str = "academic") -> str:
        """润色文本"""
        # 直接调用润色工具，避免agent路由错误
        query = f"文本:{text} 风格:{style}"
        return self.polish_tool._run(query)
    
    def generate_abstract(self, content: str, word_limit: int = 300) -> str:
        """生成摘要"""
        return self.agent.run(f"使用generate_abstract工具生成摘要，内容：{content[:2000]}，字数限制：{word_limit}")