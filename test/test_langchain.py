#测试langchain
from langchain_ollama import OllamaLLM
from langchain_core.callbacks import StreamingStdOutCallbackHandler

#初始化ollama模型
llm = OllamaLLM(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.7,
    callbacks=[StreamingStdOutCallbackHandler()],   #流式输出
)

response = llm.invoke("简要解释一下什么是人工智能")
print("\n完整回复：", response)