<template>
  <div class="rag-management">
    <div class="page-header">
      <h1>RAG系统管理</h1>
      <p>知识库管理和文档检索增强生成</p>

      <div class="header-actions">
        <el-button type="primary" @click="showCreateKBDialog = true">
          <el-icon><Plus /></el-icon>
          创建知识库
        </el-button>
        <el-button @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <div class="content">
      <!-- 知识库列表 -->
      <div class="knowledge-bases-section">
        <div class="section-header">
          <h2>知识库列表</h2>
          <el-space>
            <el-select v-model="selectedStatus" placeholder="筛选状态" @change="filterKnowledgeBases">
              <el-option label="全部" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="非活跃" value="inactive" />
            </el-select>
            <el-button @click="refreshKnowledgeBases">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
        </div>

        <div class="knowledge-bases-grid">
          <div
            v-for="kb in filteredKnowledgeBases"
            :key="kb.id"
            class="kb-card"
            @click="selectKnowledgeBase(kb)"
          >
            <div class="kb-header">
              <div class="kb-name">
                <h3>{{ kb.name }}</h3>
                <p>{{ kb.description }}</p>
              </div>
              <el-tag :type="kb.status === 'active' ? 'success' : 'info'">
                {{ kb.status === 'active' ? '活跃' : '非活跃' }}
              </el-tag>
            </div>

            <div class="kb-info">
              <div class="info-item">
                <span class="label">向量存储:</span>
                <span class="value">{{ getVectorStoreName(kb.vector_store_type) }}</span>
              </div>
              <div class="info-item">
                <span class="label">嵌入模型:</span>
                <span class="value">{{ getEmbeddingModelName(kb.embedding_model) }}</span>
              </div>
              <div class="info-item">
                <span class="label">文档数量:</span>
                <span class="value">{{ kb.document_count }}</span>
              </div>
              <div class="info-item">
                <span class="label">向量数量:</span>
                <span class="value">{{ kb.vector_count }}</span>
              </div>
            </div>

            <div class="kb-stats">
              <div class="stat">
                <span class="stat-label">最后索引</span>
                <span class="stat-value">{{ formatDate(kb.last_indexed) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">创建时间</span>
                <span class="stat-value">{{ formatDate(kb.created_at) }}</span>
              </div>
            </div>

            <div class="kb-actions">
              <el-button size="small" @click.stop="editKnowledgeBase(kb)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="primary" @click.stop="searchInKB(kb)">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button size="small" @click.stop="viewDocuments(kb)">
                <el-icon><Document /></el-icon>
                文档
              </el-button>
              <el-button size="small" type="danger" @click.stop="deleteKnowledgeBase(kb)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索区域 -->
      <div class="search-section" v-if="showSearchArea">
        <div class="section-header">
          <h2>文档搜索</h2>
          <el-button @click="showSearchArea = false">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>

        <div class="search-form">
          <el-form :model="searchForm" label-width="100px">
            <el-form-item label="搜索查询">
              <el-input
                v-model="searchForm.query"
                placeholder="请输入搜索内容"
                @keyup.enter="performSearch"
              >
                <template #append>
                  <el-button @click="performSearch">
                    <el-icon><Search /></el-icon>
                    搜索
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="知识库">
              <el-select v-model="searchForm.knowledge_base_id" placeholder="选择知识库">
                <el-option
                  v-for="kb in activeKnowledgeBases"
                  :key="kb.id"
                  :label="kb.name"
                  :value="kb.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="返回数量">
              <el-input-number
                v-model="searchForm.top_k"
                :min="1"
                :max="20"
                controls-position="right"
              />
            </el-form-item>

            <el-form-item label="相似度阈值">
              <el-slider
                v-model="searchForm.similarity_threshold"
                :min="0"
                :max="1"
                :step="0.1"
                show-input
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 搜索结果 -->
        <div class="search-results" v-if="searchResults.length > 0">
          <h3>搜索结果 ({{ searchResults.length }} 条)</h3>
          <div class="results-list">
            <div
              v-for="(result, index) in searchResults"
              :key="index"
              class="result-item"
            >
              <div class="result-header">
                <span class="result-score">相似度: {{ result.score.toFixed(3) }}</span>
                <span class="result-source">{{ result.source }}</span>
              </div>
              <div class="result-content">{{ result.content }}</div>
              <div class="result-metadata">
                <el-tag
                  v-for="(value, key) in result.metadata"
                  :key="key"
                  size="small"
                  class="metadata-tag"
                >
                  {{ key }}: {{ value }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateKBDialog"
      title="创建知识库"
      width="600px"
    >
      <KnowledgeBaseForm
        :knowledge-base="newKnowledgeBase"
        @submit="createKnowledgeBase"
        @cancel="showCreateKBDialog = false"
      />
    </el-dialog>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
    >
      <DocumentUpload
        :knowledge-bases="activeKnowledgeBases"
        @submit="uploadDocuments"
        @cancel="showUploadDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElButton, ElIcon, ElSpace, ElSelect, ElOption, ElTag, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSlider, ElMessage } from 'element-plus'
import { Plus, Upload, Refresh, Edit, Search, Document, Delete, Close } from '@element-plus/icons-vue'
import { useRAGStore } from '@/stores/rag'
import type { KnowledgeBase, RAGQuery } from '@/types/rag'
import KnowledgeBaseForm from '@/components/RAGManagement/KnowledgeBaseForm.vue'
import DocumentUpload from '@/components/RAGManagement/DocumentUpload.vue'

const ragStore = useRAGStore()

// 状态
const selectedStatus = ref('')
const showCreateKBDialog = ref(false)
const showUploadDialog = ref(false)
const showSearchArea = ref(false)
const selectedKB = ref<KnowledgeBase | null>(null)
const newKnowledgeBase = ref<Partial<KnowledgeBase>>({})
const searchForm = ref<RAGQuery>({
  query: '',
  knowledge_base_id: '',
  top_k: 5,
  similarity_threshold: 0.7
})

// 计算属性
const knowledgeBases = computed(() => ragStore.knowledgeBases)
const activeKnowledgeBases = computed(() => ragStore.activeKnowledgeBases)
const searchResults = computed(() => ragStore.searchResults)
const loading = computed(() => ragStore.loading)

const filteredKnowledgeBases = computed(() => {
  if (!selectedStatus.value) return knowledgeBases.value
  return knowledgeBases.value.filter(kb => kb.status === selectedStatus.value)
})

// 生命周期
onMounted(() => {
  loadData()
})

// 数据加载
const loadData = async () => {
  try {
    await ragStore.listKnowledgeBases()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const refreshKnowledgeBases = () => {
  ragStore.listKnowledgeBases()
}

// 知识库操作
const selectKnowledgeBase = (kb: KnowledgeBase) => {
  selectedKB.value = kb
}

const editKnowledgeBase = (kb: KnowledgeBase) => {
  // 实现编辑逻辑
  console.log('编辑知识库:', kb)
}

const deleteKnowledgeBase = async (kb: KnowledgeBase) => {
  try {
    await ragStore.deleteKnowledgeBase(kb.id)
    ElMessage.success('知识库删除成功')
  } catch (error) {
    ElMessage.error('删除知识库失败')
  }
}

const searchInKB = (kb: KnowledgeBase) => {
  selectedKB.value = kb
  searchForm.value.knowledge_base_id = kb.id
  showSearchArea.value = true
}

const viewDocuments = (kb: KnowledgeBase) => {
  // 实现查看文档逻辑
  console.log('查看文档:', kb)
}

const createKnowledgeBase = async (kbData: Partial<KnowledgeBase>) => {
  try {
    await ragStore.createKnowledgeBase(kbData)
    showCreateKBDialog.value = false
    newKnowledgeBase.value = {}
    ElMessage.success('知识库创建成功')
  } catch (error) {
    ElMessage.error('创建知识库失败')
  }
}

const uploadDocuments = async (uploadData: any) => {
  try {
    await ragStore.uploadDocuments(uploadData.kbId, uploadData.documents)
    showUploadDialog.value = false
    ElMessage.success('文档上传成功')
  } catch (error) {
    ElMessage.error('上传文档失败')
  }
}

// 搜索功能
const performSearch = async () => {
  if (!searchForm.value.query || !searchForm.value.knowledge_base_id) {
    ElMessage.warning('请填写搜索查询和选择知识库')
    return
  }

  try {
    await ragStore.searchDocuments(searchForm.value)
    ElMessage.success('搜索完成')
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

// 工具方法
const getVectorStoreName = (type: string) => {
  const names: Record<string, string> = {
    'pinecone': 'Pinecone',
    'weaviate': 'Weaviate',
    'qdrant': 'Qdrant',
    'chroma': 'Chroma',
    'faiss': 'FAISS'
  }
  return names[type] || type
}

const getEmbeddingModelName = (type: string) => {
  const names: Record<string, string> = {
    'openai': 'OpenAI',
    'huggingface': 'HuggingFace',
    'local': '本地模型'
  }
  return names[type] || type
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未索引'
  return new Date(dateString).toLocaleString()
}

const filterKnowledgeBases = () => {
  // 筛选逻辑已在计算属性中处理
}
</script>

<style scoped>
.rag-management {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.knowledge-bases-section,
.search-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.knowledge-bases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  padding: 24px;
}

.kb-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.kb-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.kb-name h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.kb-name p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.kb-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

.kb-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.kb-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.search-form {
  padding: 24px;
}

.search-results {
  padding: 0 24px 24px;
}

.search-results h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-score {
  font-size: 12px;
  color: #409EFF;
  font-weight: 600;
}

.result-source {
  font-size: 12px;
  color: #909399;
}

.result-content {
  color: #303133;
  line-height: 1.6;
  margin-bottom: 12px;
}

.result-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.metadata-tag {
  font-size: 12px;
}

@media (max-width: 768px) {
  .knowledge-bases-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
