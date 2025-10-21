<template>
  <div class="document-upload">
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
      <!-- 知识库选择 -->
      <el-form-item label="目标知识库" prop="kbId">
        <el-select v-model="formData.kbId" placeholder="请选择知识库" style="width: 100%">
          <el-option
            v-for="kb in knowledgeBases"
            :key="kb.id"
            :label="kb.name"
            :value="kb.id"
          />
        </el-select>
      </el-form-item>

      <!-- 上传方式选择 -->
      <el-form-item label="上传方式">
        <el-radio-group v-model="uploadMethod" @change="onUploadMethodChange">
          <el-radio label="file">文件上传</el-radio>
          <el-radio label="text">文本输入</el-radio>
          <el-radio label="url">URL抓取</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 文件上传 -->
      <template v-if="uploadMethod === 'file'">
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :file-list="fileList"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            multiple
            accept=".txt,.pdf,.doc,.docx,.md"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 txt, pdf, doc, docx, md 格式文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </template>

      <!-- 文本输入 -->
      <template v-if="uploadMethod === 'text'">
        <el-form-item label="文档标题">
          <el-input v-model="formData.title" placeholder="请输入文档标题" />
        </el-form-item>

        <el-form-item label="文档内容">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文档内容"
          />
        </el-form-item>
      </template>

      <!-- URL抓取 -->
      <template v-if="uploadMethod === 'url'">
        <el-form-item label="URL列表">
          <el-input
            v-model="formData.urls"
            type="textarea"
            :rows="5"
            placeholder="请输入URL，每行一个"
          />
        </el-form-item>
      </template>

      <!-- 文档元数据 -->
      <el-divider>文档元数据</el-divider>

      <el-form-item label="标签">
        <el-input
          v-model="formData.tags"
          placeholder="请输入标签，用逗号分隔"
        />
      </el-form-item>

      <el-form-item label="作者">
        <el-input v-model="formData.author" placeholder="请输入作者" />
      </el-form-item>

      <el-form-item label="来源">
        <el-input v-model="formData.source" placeholder="请输入来源" />
      </el-form-item>

      <el-form-item label="语言">
        <el-select v-model="formData.language" placeholder="选择语言">
          <el-option label="中文" value="zh" />
          <el-option label="英文" value="en" />
          <el-option label="日文" value="ja" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>

      <!-- 处理选项 -->
      <el-divider>处理选项</el-divider>

      <el-form-item label="自动分块">
        <el-switch v-model="formData.autoChunk" />
        <span class="form-tip">是否自动将文档分块处理</span>
      </el-form-item>

      <el-form-item label="分块大小" v-if="formData.autoChunk">
        <el-input-number
          v-model="formData.chunkSize"
          :min="100"
          :max="2000"
          controls-position="right"
          style="width: 100%"
        />
        <span class="form-tip">字符数</span>
      </el-form-item>

      <el-form-item label="分块重叠" v-if="formData.autoChunk">
        <el-input-number
          v-model="formData.chunkOverlap"
          :min="0"
          :max="500"
          controls-position="right"
          style="width: 100%"
        />
        <span class="form-tip">字符数</span>
      </el-form-item>

      <el-form-item label="立即索引">
        <el-switch v-model="formData.immediateIndex" />
        <span class="form-tip">是否立即创建向量索引</span>
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-space>
          <el-button type="primary" @click="submitForm" :loading="uploading">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$emit('cancel')">取消</el-button>
        </el-space>
      </el-form-item>
    </el-form>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="uploadProgress" />
      <p>{{ uploadStatus }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElDivider, ElInputNumber, ElSwitch, ElSpace, ElIcon, ElUpload, ElProgress, ElRadioGroup, ElRadio } from 'element-plus'
import { UploadFilled, Upload } from '@element-plus/icons-vue'
import type { KnowledgeBase, Document } from '@/types/rag'

interface Props {
  knowledgeBases: KnowledgeBase[]
}

interface Emits {
  (e: 'submit', data: any): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()
const uploadRef = ref()

// 状态
const uploadMethod = ref('file')
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')

// 表单数据
const formData = reactive({
  kbId: '',
  title: '',
  content: '',
  urls: '',
  tags: '',
  author: '',
  source: '',
  language: 'zh',
  autoChunk: true,
  chunkSize: 1000,
  chunkOverlap: 200,
  immediateIndex: true
})

// 表单验证规则
const rules = {
  kbId: [
    { required: true, message: '请选择知识库', trigger: 'change' }
  ]
}

// 上传方式变化处理
const onUploadMethodChange = (method: string) => {
  // 重置表单数据
  formData.title = ''
  formData.content = ''
  formData.urls = ''
  fileList.value = []
}

// 文件处理
const handleFileChange = (file: any, fileList: any[]) => {
  console.log('文件变化:', file, fileList)
}

const handleFileRemove = (file: any, fileList: any[]) => {
  console.log('文件移除:', file, fileList)
}

// 表单提交
const submitForm = async () => {
  try {
    await formRef.value.validate()

    uploading.value = true
    uploadProgress.value = 0
    uploadStatus.value = '准备上传...'

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
        uploadStatus.value = `上传中... ${uploadProgress.value}%`
      }
    }, 200)

    // 根据上传方式处理数据
    let documents: Document[] = []

    if (uploadMethod.value === 'file') {
      // 处理文件上传
      documents = await processFiles()
    } else if (uploadMethod.value === 'text') {
      // 处理文本输入
      documents = [{
        id: `doc_${Date.now()}`,
        content: formData.content,
        metadata: {
          title: formData.title,
          author: formData.author,
          source: formData.source,
          tags: formData.tags.split(',').map(t => t.trim()),
          language: formData.language
        },
        chunks: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }]
    } else if (uploadMethod.value === 'url') {
      // 处理URL抓取
      documents = await processUrls()
    }

    // 完成上传
    clearInterval(progressInterval)
    uploadProgress.value = 100
    uploadStatus.value = '上传完成'

    setTimeout(() => {
      uploading.value = false
      emit('submit', {
        kbId: formData.kbId,
        documents,
        options: {
          autoChunk: formData.autoChunk,
          chunkSize: formData.chunkSize,
          chunkOverlap: formData.chunkOverlap,
          immediateIndex: formData.immediateIndex
        }
      })
    }, 1000)

  } catch (error) {
    uploading.value = false
    console.error('上传失败:', error)
  }
}

// 处理文件
const processFiles = async (): Promise<Document[]> => {
  const documents: Document[] = []

  for (const file of fileList.value) {
    const content = await readFileContent(file.raw)
    documents.push({
      id: `doc_${Date.now()}_${Math.random()}`,
      content,
      metadata: {
        title: file.name,
        author: formData.author,
        source: formData.source,
        tags: formData.tags.split(',').map(t => t.trim()),
        language: formData.language
      },
      chunks: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
  }

  return documents
}

// 处理URL
const processUrls = async (): Promise<Document[]> => {
  const urls = formData.urls.split('\n').filter(url => url.trim())
  const documents: Document[] = []

  for (const url of urls) {
    // 这里应该实现URL内容抓取逻辑
    documents.push({
      id: `doc_${Date.now()}_${Math.random()}`,
      content: `从 ${url} 抓取的内容`,
      metadata: {
        title: `URL: ${url}`,
        author: formData.author,
        source: url,
        tags: formData.tags.split(',').map(t => t.trim()),
        language: formData.language
      },
      chunks: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
  }

  return documents
}

// 读取文件内容
const readFileContent = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      resolve(e.target?.result as string)
    }
    reader.onerror = reject
    reader.readAsText(file)
  })
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
  fileList.value = []
  uploadMethod.value = 'file'
}
</script>

<style scoped>
.document-upload {
  padding: 20px 0;
}

.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin-top: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.upload-progress p {
  margin: 8px 0 0 0;
  color: #606266;
  font-size: 14px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-divider) {
  margin: 20px 0 16px 0;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
