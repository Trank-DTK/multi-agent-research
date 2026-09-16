# 模型设置与升级

升级后在 bakend 目录安装 requirements.txt 中依赖并运行 `python manage.py migrate`，然后重启后端。生产环境需要重建前后端容器以应用上传限制与超时配置。

登录后点击侧栏底部用户名 → 设置，可添加多个供应商与模型，选择默认配置。支持 DeepSeek、OpenRouter、Qwen、OpenAI、Ollama、LM Studio 和自定义 OpenAI 兼容服务。模型 ID 应填写供应商实际提供的 ID。保存后可测试连接。

API Key 按用户存储并在后端加密，不返回浏览器。部署时设置稳定的 MODEL_KEY_SECRET；更换该值后需重新录入已有密钥。修改服务地址时需重新填写或明确清除密钥，避免将旧密钥发送到新地址。

Ollama 使用原生 `/api/chat`，默认地址 http://localhost:11434；LM Studio 使用 OpenAI 兼容接口，默认地址 http://localhost:1234/v1。地址由后端访问：Docker 内的 localhost 指向容器自身，Windows Docker Desktop 访问宿主机可使用 host.docker.internal。模型须在本地服务中先下载并启用。

PDF 上传不再依赖本地向量模型，上传后提取文本并分块。当前文献问答以关键词匹配检索文本片段；扫描 PDF 需先 OCR。选择研究资料后，模型只接收所选资料的有限片段，并非整篇全文。云端模型实际连接需使用自己的密钥进行验证。

隔离回归测试：`python manage.py test accounts documents chat writing.test_sections --settings=bakend.test_settings`。测试使用内存数据库与模拟模型，不修改真实账号或调用付费服务。
