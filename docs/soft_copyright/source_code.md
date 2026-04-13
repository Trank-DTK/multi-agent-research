# 多智能体科研协作平台 - 源代码文档

## 一、软件基本信息

| 项目 | 内容 |
|------|------|
| 软件名称 | 多智能体科研协作平台 |
| 英文名称 | Multi-Agent Research Assistant |
| 版本号 | V1.0 |
| 开发语言 | Python 3.11, JavaScript (Vue3) |
| 代码行数 | 约15000行 |
| 开发周期 | 12周 |

## 二、目录结构
```bash
multi_agent_research/
├── bakend/ # Django后端 (约8000行)
│ ├── accounts/ # 用户认证模块
│ ├── agents/ # 智能体核心模块
│ ├── chat/ # 对话模块
│ ├── documents/ # 文献管理模块
│ ├── analysis/ # 数据分析模块
│ └── writing/ # 论文写作模块
├── frontend/ # Vue前端 (约7000行)
│ ├── src/
│ │ ├── views/ # 页面组件
│ │ ├── components/ # 公共组件
│ │ ├── stores/ # 状态管理
│ │ └── utils/ # 工具函数
└── test/ # 测试代码
```


## 三、核心代码

### 3.1 后端核心代码

#### 3.1.1 智能体基类 (agents/agent.py)

```python
# 第50-100行示例
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
```

