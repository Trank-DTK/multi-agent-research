from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from .tools import CurrentTimeTool, RandomNumberTool, CalculatorTool

def get_ollama_base_url():
    """获取Ollama地址"""
    import os
    import platform
    
    if os.path.exists('/.dockerenv'):
        if platform.system() in ['Windows', 'Darwin']:
            return os.environ.get('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')
        else:
            return os.environ.get('OLLAMA_BASE_URL', 'http://172.17.0.1:11434')
    return os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')


def create_agent(llm=None, verbose=True, memory=None):
    """创建智能体实例"""
    if llm is None:
        llm = Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.7
        )
    
    tools = [
        CurrentTimeTool(),
        RandomNumberTool(),
        CalculatorTool(),
    ]
    
    if memory is None:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,   #对话式Agent
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    return agent


if __name__=="__main__":
    agent = create_agent(verbose=True)
    # 第一轮对话
    response1 = agent.run("现在几点了？")
    print(response1)

    # 第二轮对话（Agent 会记住刚才的对话）
    response2 = agent.run("我刚才问了你什么？")
    print(response2)

    # 第三轮：多步推理
    response3 = agent.run("计算 123 * 456 的结果，然后告诉我结果是否大于 50000")
    print(response3)