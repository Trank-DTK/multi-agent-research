from langchain_classic.agents import load_tools, initialize_agent, AgentType
from langchain_community.llms import Ollama

llm = Ollama(model="qwen2.5:7b", temperature=0)
tools = load_tools(["llm-math", "arxiv"], llm=llm)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
response = agent.run("计算 123 * 456 的结果")
print(response)