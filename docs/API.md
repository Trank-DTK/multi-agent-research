 # API文档
 
 ## 基础信息
 
 - Base URL: `/api`
 - 认证方式: JWT Bearer Token
 
 ## 认证接口
 
 ### 用户注册
 - **URL**: `/auth/register/`
 - **Method**: `POST`
 - **Request**:
 ```json
 {
   "username": "string",
   "password": "string",
   "password2": "string",
   "email": "string"
 }
 ```
 - **Response**:
 ```json
 {
   "user": {
     "id": 1,
     "username": "string",
     "email": "string"
   },
   "message": "注册成功"
 }
 ```
 
 ### 用户登录
 - **URL**: `/auth/login/`
 - **Method**: `POST`
 - **Request**:
 ```json
 {
   "username": "string",
   "password": "string"
 }
 ```
 - **Response**:
 ```json
 {
   "access": "eyJhbGciOiJIUzI1NiIs...",
   "refresh": "eyJhbGciOiJIUzI1NiIs..."
 }
 ```
 
 ### 刷新Token
 - **URL**: `/auth/refresh/`
 - **Method**: `POST`
 - **Request**:
 ```json
 {
   "refresh": "eyJhbGciOiJIUzI1NiIs..."
 }
 ```
 - **Response**:
 ```json
 {
   "access": "eyJhbGciOiJIUzI1NiIs..."
 }
 ```
 
 ### 获取当前用户信息
 - **URL**: `/auth/user/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "id": 1,
   "username": "string",
   "email": "string",
   "first_name": "string",
   "last_name": "string"
 }
 ```
 
 ---
 
 ## 对话接口
 
 ### 发送消息（非流式）
 - **URL**: `/chat/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "message": "你好，请介绍一下自己",
   "conversation_id": 1
 }
 ```
 - **Response**:
 ```json
 {
   "response": "你好！我是AI助手...",
   "conversation_id": 1
 }
 ```
 
 ### 发送消息（流式）
 - **URL**: `/chat/stream/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "message": "写一首关于春天的诗"
 }
 ```
 - **Response**: Server-Sent Events (SSE)
 ```
 data: {"token": "春"}
 data: {"token": "天"}
 data: {"token": "来"}
 data: {"token": "了"}
 ...
 data: [DONE]
 ```
 
 ### 获取对话列表
 - **URL**: `/chat/conversations/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 [
   {
     "id": 1,
     "title": "关于深度学习的讨论",
     "created_at": "2024-01-01T10:00:00Z",
     "updated_at": "2024-01-01T10:05:00Z"
   }
 ]
 ```
 
 ### 获取对话详情
 - **URL**: `/chat/conversations/{conversation_id}/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 [
   {
     "id": 1,
     "role": "user",
     "content": "你好",
     "created_at": "2024-01-01T10:00:00Z"
   },
   {
     "id": 2,
     "role": "assistant",
     "content": "你好！有什么我可以帮你的？",
     "created_at": "2024-01-01T10:00:01Z"
   }
 ]
 ```
 
 ### 删除对话
 - **URL**: `/chat/conversations/{conversation_id}/delete/`
 - **Method**: `DELETE`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "message": "删除成功"
 }
 ```
 
 ---
 
 ## 智能体接口
 
 ### Agent聊天
 - **URL**: `/agent/chat/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "message": "现在几点了？",
   "conversation_id": 1
 }
 ```
 - **Response**:
 ```json
 {
   "response": "当前时间是 14:30:25",
   "conversation_id": 1
 }
 ```
 
 ### 重置Agent对话
 - **URL**: `/agent/reset/{conversation_id}/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "message": "对话已重置"
 }
 ```
 
 ---
 
 ## 文献管理接口
 
 ### 上传PDF文献
 - **URL**: `/documents/upload/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Content-Type**: `multipart/form-data`
 - **Request**:
 | 参数 | 类型 | 说明 |
 |------|------|------|
 | file | File | PDF文件 |
 | title | String | 文献标题（可选） |
 - **Response**:
 ```json
 {
   "message": "上传成功",
   "document": {
     "id": 1,
     "title": "深度学习综述",
     "file_name": "paper.pdf",
     "page_count": 15
   },
   "chunk_count": 25
 }
 ```
 
 ### 获取文献列表
 - **URL**: `/documents/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 [
   {
     "id": 1,
     "title": "深度学习综述",
     "file_name": "paper.pdf",
     "uploaded_at": "2024-01-01T10:00:00Z"
   }
 ]
 ```
 
 ### 删除文献
 - **URL**: `/documents/{document_id}/delete/`
 - **Method**: `DELETE`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "message": "删除成功"
 }
 ```
 
 ### 文献检索
 - **URL**: `/documents/search/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "query": "深度学习在图像识别中的应用",
   "top_k": 5
 }
 ```
 - **Response**:
 ```json
 {
   "query": "深度学习在图像识别中的应用",
   "results": [
     {
       "document_id": 1,
       "document_title": "深度学习综述",
       "content": "深度学习在图像识别领域取得了突破性进展...",
       "score": 0.89
     }
   ]
 }
 ```
 
 ---
 
 ## 文献助手接口
 
 ### 文献助手对话
 - **URL**: `/literature/chat/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "message": "帮我找一下关于深度学习的文献",
   "conversation_id": 1
 }
 ```
 - **Response**:
 ```json
 {
   "response": "找到以下相关内容：\n[1] 来自《深度学习综述》...",
   "conversation_id": 1
 }
 ```
 
 ### 重置文献助手对话
 - **URL**: `/literature/reset/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "message": "对话已重置"
 }
 ```
 
 ---
 
 ## 协作研究接口
 
 ### 协作研究（带评审）
 - **URL**: `/collaboration/review/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "question": "如何提高深度学习模型在图像分类中的准确率？",
   "conversation_id": 1
 }
 ```
 - **Response**:
 ```json
 {
   "response": "# 研究方案报告\n\n## 研究问题\n如何提高...",
   "conversation_id": 1,
   "evaluation": {
     "overall_score": 7.5,
     "passed": true,
     "suggestions": ["建议使用数据增强", "建议调整学习率"],
     "dimensions": {
       "literature_review": 8,
       "experiment_design": 7,
       "consistency": 8,
       "feasibility": 7
     }
   },
   "improved": false
 }
 ```
 
 ---
 
 ## 数据分析接口
 
 ### 上传数据集
 - **URL**: `/datasets/upload/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Content-Type**: `multipart/form-data`
 - **Request**:
 | 参数 | 类型 | 说明 |
 |------|------|------|
 | file | File | CSV/Excel文件 |
 | name | String | 数据集名称（可选） |
 - **Response**:
 ```json
 {
   "message": "上传成功",
   "dataset": {
     "id": 1,
     "name": "销售数据",
     "row_count": 1000,
     "column_count": 5
   },
   "preview": [...],
   "insight": "数据包含1000行5列..."
 }
 ```
 
 ### 获取数据集列表
 - **URL**: `/datasets/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 [
   {
     "id": 1,
     "name": "销售数据",
     "row_count": 1000,
     "uploaded_at": "2024-01-01T10:00:00Z"
   }
 ]
 ```
 
 ### 数据分析
 - **URL**: `/datasets/{dataset_id}/analyze/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "analysis_type": "descriptive",
   "columns": ["age", "salary"]
 }
 ```
 - **Response**:
 ```json
 {
   "result": {
     "statistics": {...},
     "missing_values": {...}
   },
   "insight": "年龄分布在18-65岁之间，平均35.2岁",
   "analysis_id": 1
 }
 ```
 
 ### 生成图表
 - **URL**: `/datasets/{dataset_id}/visualize/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "chart_type": "bar",
   "x_column": "category",
   "y_column": "value",
   "title": "各类别销售额"
 }
 ```
 - **Response**:
 ```json
 {
   "chart_data": {
     "x": ["A", "B", "C"],
     "y": [100, 200, 150]
   },
   "chart_type": "bar",
   "title": "各类别销售额",
   "visualization_id": 1
 }
 ```
 
 ---
 
 ## 论文写作接口
 
 ### 生成论文大纲
 - **URL**: `/writing/outline/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "topic": "深度学习在图像识别中的应用",
   "paper_type": "research"
 }
 ```
 - **Response**:
 ```json
 {
   "outline": "# 深度学习在图像识别中的应用\n\n## 1. 引言\n..."
 }
 ```
 
 ### 创建论文
 - **URL**: `/writing/papers/create/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "title": "深度学习综述",
   "topic": "深度学习技术"
 }
 ```
 - **Response**:
 ```json
 {
   "id": 1,
   "title": "深度学习综述",
   "status": "draft",
   "created_at": "2024-01-01T10:00:00Z"
 }
 ```
 
 ### 获取论文列表
 - **URL**: `/writing/papers/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 [
   {
     "id": 1,
     "title": "深度学习综述",
     "status": "draft",
     "updated_at": "2024-01-01T10:00:00Z"
   }
 ]
 ```
 
 ### 获取论文详情
 - **URL**: `/writing/papers/{paper_id}/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**:
 ```json
 {
   "id": 1,
   "title": "深度学习综述",
   "abstract": "",
   "content": "",
   "sections": [...]
 }
 ```
 
 ### 撰写章节
 - **URL**: `/writing/papers/{paper_id}/section/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "title": "引言",
   "context": "研究背景：深度学习近年来发展迅速...",
   "word_count": 500
 }
 ```
 - **Response**:
 ```json
 {
   "section_id": 1,
   "title": "引言",
   "content": "深度学习是机器学习的一个分支..."
 }
 ```
 
 ### 润色文本
 - **URL**: `/writing/polish/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "text": "我们做了一个实验，结果很好。",
   "style": "academic"
 }
 ```
 - **Response**:
 ```json
 {
   "polished": "实验结果表明，该方法在测试集上取得了优异的性能。"
 }
 ```
 
 ### 生成摘要
 - **URL**: `/writing/papers/{paper_id}/abstract/`
 - **Method**: `POST`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Request**:
 ```json
 {
   "content": "论文完整内容...",
   "word_limit": 300
 }
 ```
 - **Response**:
 ```json
 {
   "abstract": "本文研究了深度学习在图像识别中的应用..."
 }
 ```
 
 ### 导出Word文档
 - **URL**: `/writing/papers/{paper_id}/export/`
 - **Method**: `GET`
 - **Headers**: `Authorization: Bearer <access_token>`
 - **Response**: Word文档文件下载
 
 ---
 
 ## 状态码说明
 
 | 状态码 | 说明 |
 |--------|------|
 | 200 | 请求成功 |
 | 201 | 创建成功 |
 | 400 | 请求参数错误 |
 | 401 | 未认证（Token无效或过期） |
 | 403 | 权限不足 |
 | 404 | 资源不存在 |
 | 429 | 请求过于频繁 |
 | 500 | 服务器内部错误 |
 
 ---
 
 ## 错误响应格式
 
 ```json
 {
   "code": 400,
   "message": "错误描述",
   "details": {
     "field": "具体错误信息"
   }
 }
 ```
 
 ---
 
 *文档版本: v1.0.0*
 *最后更新: 2026年4月13日*