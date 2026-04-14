<!-- 文献管理页面 -->
<template>
  <div class="documents-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/dashboard')">
        <span class="btn-icon">←</span>
        <span class="btn-text">返回主页</span>
      </button>
      <div class="header-content">
        <h1>📚 文献库管理</h1>
        <p class="subtitle">管理您的科研文献，支持PDF上传和分析</p>
        <button @click="showUpload = true" class="upload-btn">
          <span class="btn-icon">+</span>
          <span class="btn-text">上传文献</span>
        </button>
      </div>
    </div>
    
    <!-- 上传弹窗 -->
    <div v-if="showUpload" class="modal">
      <div class="modal-content">
        <h3>上传PDF文献</h3>
        <input type="file" accept=".pdf" @change="onFileSelected" ref="fileInput" />
        <input v-model="uploadTitle" placeholder="文献标题（可选）" />
        <div class="modal-buttons">
          <button @click="uploadFile" :disabled="uploading">{{ uploading ? '上传中...' : '确认上传' }}</button>
          <button @click="showUpload = false">取消</button>
        </div>
        <p v-if="uploadError" class="error">{{ uploadError }}</p>
        <p v-if="uploadSuccess" class="success">{{ uploadSuccess }}</p>
      </div>
    </div>
    
    <!-- 文献列表 -->
    <div class="document-list">
      <div v-for="doc in documents" :key="doc.id" class="document-card">
        <div class="doc-info">
          <h3>{{ doc.title }}</h3>
          <p>文件名：{{ doc.file_name }}</p>
          <p>页数：{{ doc.page_count }} 页</p>
          <p>上传时间：{{ formatDate(doc.uploaded_at) }}</p>
        </div>
        <div class="doc-actions">
          <button @click="deleteDocument(doc.id)" class="delete-btn">删除</button>
        </div>
      </div>
      <div v-if="documents.length === 0" class="empty">
        暂无文献，点击上方按钮上传
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'

const documents = ref([])
const showUpload = ref(false)
const uploading = ref(false)
const uploadTitle = ref('')
const uploadError = ref('')
const uploadSuccess = ref('')
const fileInput = ref(null)
const selectedFile = ref(null)

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchDocuments = async () => {
  try {
    const res = await axios.get('/documents/')
    documents.value = res.data
  } catch (error) {
    console.error('获取文献列表失败', error)
  }
}

const onFileSelected = (e) => {
  selectedFile.value = e.target.files[0]
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    uploadError.value = '请选择PDF文件'
    return
  }
  
  uploading.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  if (uploadTitle.value) {
    formData.append('title', uploadTitle.value)
  }
  
  try {
    const res = await axios.post('/documents/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    uploadSuccess.value = `上传成功！已处理 ${res.data.chunk_count} 个文本块`
    setTimeout(() => {
      showUpload.value = false
      uploadSuccess.value = ''
      uploadTitle.value = ''
      selectedFile.value = null
      if (fileInput.value) fileInput.value.value = ''
      fetchDocuments()
    }, 2000)
    
  } catch (error) {
    uploadError.value = error.response?.data?.error || '上传失败'
  } finally {
    uploading.value = false
  }
}

const deleteDocument = async (docId) => {
  if (!confirm('确定要删除这篇文献吗？')) return
  
  try {
    await axios.delete(`/documents/${docId}/delete/`)
    fetchDocuments()
  } catch (error) {
    console.error('删除失败', error)
  }
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  max-width: 1000px;
  margin: 30px auto;
  padding: 0 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.upload-btn {
  padding: 10px 20px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  width: 400px;
}

.modal-content input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.document-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: white;
}

.doc-info h3 {
  margin: 0 0 5px;
  font-size: 16px;
}

.doc-info p {
  margin: 3px 0;
  color: #666;
  font-size: 12px;
}

.delete-btn {
  padding: 8px 16px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}

.error {
  color: #f44336;
  margin-top: 10px;
}

.success {
  color: #1890ff;
  margin-top: 10px;
}
</style>