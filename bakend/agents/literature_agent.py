# 文献助手Agent
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from .literature_tools import SearchLiteratureTool, SummarizeDocumentTool
from .agent import get_ollama_base_url

def create_literature_agent(user, memory=None, verbose=True):
    """创建文献助手Agent"""

    llm = OllamaLLM(
        model="qwen2.5:7b",
        base_url=get_ollama_base_url(),
        temperature=0.7
    )

    tools = [
        SearchLiteratureTool(user),
        SummarizeDocumentTool(user),
    ]

    # memory=None表示不使用记忆，减少内存占用
    if memory is None:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,  #有记忆，可使用工具，ReAct类型
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True   #自动捕获异常并调试
    )

    return agent