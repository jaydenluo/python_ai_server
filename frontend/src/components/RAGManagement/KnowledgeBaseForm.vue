<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
    <!-- 基本信息 -->
    <el-form-item label="知识库名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入知识库名称" />
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input
        v-model="formData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入知识库描述"
      />
    </el-form-item>

    <!-- 向量存储配置 -->
    <el-divider>向量存储配置</el-divider>

    <el-form-item label="向量存储类型" prop="vector_store_type">
      <el-select v-model="formData.vector_store_type" @change="onVectorStoreChange">
        <el-option label="Pinecone" value="pinecone" />
        <el-option label="Weaviate" value="weaviate" />
        <el-option label="Qdrant" value="qdrant" />
        <el-option label="Chroma" value="chroma" />
        <el-option label="FAISS" value="faiss" />
      </el-select>
    </el-form-item>

    <el-form-item label="嵌入模型" prop="embedding_model">
      <el-select v-model="formData.embedding_model" @change="onEmbeddingModelChange">
        <el-option label="OpenAI" value="openai" />
        <el-option label="HuggingFace" value="huggingface" />
        <el-option label="本地模型" value="local" />
      </el-select>
    </el-form-item>

    <!-- Pinecone配置 -->
    <template v-if="formData.vector_store_type === 'pinecone'">
      <el-form-item label="API密钥">
        <el-input
          v-model="formData.vector_store_config.api_key"
          type="password"
          placeholder="请输入Pinecone API密钥"
          show-password
        />
      </el-form-item>

      <el-form-item label="环境">
        <el-input
          v-model="formData.vector_store_config.environment"
          placeholder="请输入环境名称"
        />
      </el-form-item>
    </template>

    <!-- Weaviate配置 -->
    <template v-if="formData.vector_store_type === 'weaviate'">
      <el-form-item label="URL">
        <el-input
          v-model="formData.vector_store_config.url"
          placeholder="请输入Weaviate URL"
        />
      </el-form-item>

      <el-form-item label="API密钥">
        <el-input
          v-model="formData.vector_store_config.api_key"
          type="password"
          placeholder="请输入API密钥"
          show-password
        />
      </el-form-item>
    </template>

    <!-- Qdrant配置 -->
    <template v-if="formData.vector_store_type === 'qdrant'">
      <el-form-item label="URL">
        <el-input
          v-model="formData.vector_store_config.url"
          placeholder="请输入Qdrant URL"
        />
      </el-form-item>

      <el-form-item label="API密钥">
        <el-input
          v-model="formData.vector_store_config.api_key"
          type="password"
          placeholder="请输入API密钥"
          show-password
        />
      </el-form-item>
    </template>

    <!-- 文档处理配置 -->
    <el-divider>文档处理配置</el-divider>

    <el-form-item label="分块大小">
      <el-input-number
        v-model="formData.settings.chunk_size"
        :min="100"
        :max="2000"
        controls-position="right"
        style="width: 100%"
      />
      <span class="form-tip">文档分块的大小（字符数）</span>
    </el-form-item>

    <el-form-item label="分块重叠">
      <el-input-number
        v-model="formData.settings.chunk_overlap"
        :min="0"
        :max="500"
        controls-position="right"
        style="width: 100%"
      />
      <span class="form-tip">分块之间的重叠字符数</span>
    </el-form-item>

    <el-form-item label="相似度阈值">
      <el-slider
        v-model="formData.settings.similarity_threshold"
        :min="0"
        :max="1"
        :step="0.1"
        show-input
      />
      <span class="form-tip">搜索结果的最小相似度阈值</span>
    </el-form-item>

    <el-form-item label="最大结果数">
      <el-input-number
        v-model="formData.settings.max_results"
        :min="1"
        :max="50"
        controls-position="right"
        style="width: 100%"
      />
      <span class="form-tip">返回的最大搜索结果数量</span>
    </el-form-item>

    <!-- 高级配置 -->
    <el-divider>高级配置</el-divider>

    <el-form-item label="索引名称">
      <el-input
        v-model="formData.vector_store_config.index_name"
        placeholder="请输入索引名称"
      />
    </el-form-item>

    <el-form-item label="维度">
      <el-input-number
        v-model="formData.vector_store_config.dimension"
        :min="128"
        :max="4096"
        controls-position="right"
        style="width: 100%"
      />
      <span class="form-tip">向量维度（通常为1536）</span>
    </el-form-item>

    <el-form-item label="距离度量">
      <el-select v-model="formData.vector_store_config.metric">
        <el-option label="余弦相似度" value="cosine" />
        <el-option label="欧几里得距离" value="euclidean" />
        <el-option label="点积" value="dotproduct" />
      </el-select>
    </el-form-item>

    <!-- 操作按钮 -->
    <el-form-item>
      <el-space>
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="$emit('cancel')">取消</el-button>
      </el-space>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElDivider, ElInputNumber, ElSlider, ElSpace } from 'element-plus'
import type { KnowledgeBase } from '@/types/rag'

interface Props {
  knowledgeBase?: Partial<KnowledgeBase>
}

interface Emits {
  (e: 'submit', kb: Partial<KnowledgeBase>): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()

// 表单数据
const formData = reactive<Partial<KnowledgeBase>>({
  name: '',
  description: '',
  vector_store_type: 'pinecone',
  embedding_model: 'openai',
  settings: {
    chunk_size: 1000,
    chunk_overlap: 200,
    similarity_threshold: 0.7,
    max_results: 10
  },
  vector_store_config: {
    api_key: '',
    environment: '',
    url: '',
    index_name: '',
    dimension: 1536,
    metric: 'cosine'
  },
  status: 'active'
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入知识库描述', trigger: 'blur' }
  ],
  vector_store_type: [
    { required: true, message: '请选择向量存储类型', trigger: 'change' }
  ],
  embedding_model: [
    { required: true, message: '请选择嵌入模型', trigger: 'change' }
  ]
}

// 监听props变化
watch(() => props.knowledgeBase, (newKB) => {
  if (newKB) {
    Object.assign(formData, newKB)
  }
}, { immediate: true, deep: true })

// 向量存储类型变化处理
const onVectorStoreChange = (type: string) => {
  // 根据类型重置配置
  formData.vector_store_config = {
    api_key: '',
    environment: '',
    url: '',
    index_name: '',
    dimension: 1536,
    metric: 'cosine'
  }

  // 根据类型设置默认配置
  switch (type) {
    case 'pinecone':
      formData.vector_store_config.environment = 'us-west1-gcp'
      break
    case 'weaviate':
      formData.vector_store_config.url = 'http://localhost:8080'
      break
    case 'qdrant':
      formData.vector_store_config.url = 'http://localhost:6333'
      break
    case 'chroma':
      formData.vector_store_config.url = 'http://localhost:8000'
      break
  }
}

// 嵌入模型变化处理
const onEmbeddingModelChange = (model: string) => {
  // 根据模型设置默认维度
  switch (model) {
    case 'openai':
      formData.vector_store_config!.dimension = 1536
      break
    case 'huggingface':
      formData.vector_store_config!.dimension = 768
      break
    case 'local':
      formData.vector_store_config!.dimension = 512
      break
  }
}

// 表单提交
const submitForm = async () => {
  try {
    await formRef.value.validate()
    emit('submit', { ...formData })
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
}
</script>

<style scoped>
.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-divider) {
  margin: 20px 0 16px 0;
}
</style>
