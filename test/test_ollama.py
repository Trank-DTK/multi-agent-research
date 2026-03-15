import ollama

response = ollama.chat(
  model="qwen2.5:7b",
  messages=[
    {'role': 'user', 'content': '你好，请用一句话介绍一下自己'},
  ]
)

print(response['message']['content'])