# 实验助手Agent
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from .experiment_tools import (
    DesignExperimentTool, 
    ValidateHypothesisTool, 
    GenerateMethodologyTool,
    LiteratureToExperimentTool
)
from .agent import get_ollama_base_url

def create_experiment_agent(user, vector_service=None, memory=None, verbose=True):
    """创建实验助手Agent"""
    
    llm = Ollama(
        model="qwen2.5:7b",
        base_url=get_ollama_base_url(),
        temperature=0.7
    )
    
    tools = [
        DesignExperimentTool(llm=llm),
        ValidateHypothesisTool(user, vector_service=vector_service),
        GenerateMethodologyTool(llm=llm),
        LiteratureToExperimentTool(llm=llm),
    ]
    
    if memory is None:
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