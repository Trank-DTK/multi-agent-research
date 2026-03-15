#测试流式输出
import ollama

stream = ollama.chat(
  model="qwen2.5:7b",
  messages=[
    {'role': 'user', 'content': '写一首诗歌，题目是《春天的花》'},
  ],
  stream=True
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)