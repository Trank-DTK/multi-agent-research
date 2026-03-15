#测试提示词
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

llm = OllamaLLM(model="qwen2.5:7b")

#创建提示词模板
prompt = PromptTemplate(
    input_variables=["topic", "style"],    #定义输入变量
    template="请用{style}风格，写一段关于{topic}的描述，字数在50字以内"
)

#创建链
chain = prompt | llm   #将提示词和模型连接成一个链，把prompt的输出作为llm的输入

response = chain.invoke({"topic": "人工智能", "style": "幽默"})  #传入输入变量，调用链生成回复
print(response)

