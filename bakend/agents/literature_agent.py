# 文献助手Agent
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from .literature_tools import SearchLiteratureTool, SummarizeDocumentTool
from .agent import get_ollama_base_url

def create_literature_agent(user, memory=None, verbose=True):
    """创建文献助手Agent"""
    print(f"create_literature_agent: 开始创建，用户ID: {user.id}")

    try:
        llm = OllamaLLM(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.7
        )
        print("create_literature_agent: OllamaLLM 初始化成功")

        tools = [
            SearchLiteratureTool(user),
            SummarizeDocumentTool(user),
        ]
        print(f"create_literature_agent: 工具列表初始化完成，工具数量: {len(tools)}")

        # memory=None表示不使用记忆，减少内存占用
        if memory is None:
            print("create_literature_agent: 创建 ConversationBufferMemory")
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        print("create_literature_agent: 开始调用 initialize_agent")
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,  #有记忆，可使用工具，ReAct类型
            memory=memory,
            verbose=verbose,
            handle_parsing_errors=True   #自动捕获异常并调试
        )
        print("create_literature_agent: Agent 初始化成功")
        return agent

    except Exception as e:
        print(f"create_literature_agent 初始化失败: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise