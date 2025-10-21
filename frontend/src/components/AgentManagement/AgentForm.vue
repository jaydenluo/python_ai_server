<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
    <!-- 基本信息 -->
    <el-form-item label="智能体名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入智能体名称" />
    </el-form-item>

    <el-form-item label="智能体类型" prop="type">
      <el-select v-model="formData.type" placeholder="选择智能体类型" @change="onTypeChange">
        <el-option label="LangGraph" value="langgraph" />
        <el-option label="CrewAI" value="crewai" />
        <el-option label="AutoGen" value="autogen" />
      </el-select>
    </el-form-item>

    <el-form-item label="角色" prop="role">
      <el-input v-model="formData.role" placeholder="请输入角色描述" />
    </el-form-item>

    <el-form-item label="目标" prop="goal">
      <el-input
        v-model="formData.goal"
        type="textarea"
        :rows="3"
        placeholder="请输入智能体的目标"
      />
    </el-form-item>

    <el-form-item label="背景故事" prop="backstory">
      <el-input
        v-model="formData.backstory"
        type="textarea"
        :rows="3"
        placeholder="请输入智能体的背景故事"
      />
    </el-form-item>

    <!-- LLM配置 -->
    <el-divider>LLM配置</el-divider>

    <el-form-item label="提供商" prop="llm_config.provider">
      <el-select v-model="formData.llm_config.provider" @change="onProviderChange">
        <el-option label="OpenAI" value="openai" />
        <el-option label="Anthropic" value="anthropic" />
        <el-option label="本地模型" value="local" />
      </el-select>
    </el-form-item>

    <el-form-item label="模型" prop="llm_config.model">
      <el-input v-model="formData.llm_config.model" placeholder="请输入模型名称" />
    </el-form-item>

    <el-form-item label="温度" prop="llm_config.temperature">
      <el-slider
        v-model="formData.llm_config.temperature"
        :min="0"
        :max="2"
        :step="0.1"
        show-input
        show-input-controls
      />
    </el-form-item>

    <el-form-item label="最大令牌数" prop="llm_config.max_tokens">
      <el-input-number
        v-model="formData.llm_config.max_tokens"
        :min="1"
        :max="4096"
        controls-position="right"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="API密钥" v-if="formData.llm_config.provider !== 'local'">
      <el-input
        v-model="formData.llm_config.api_key"
        type="password"
        placeholder="请输入API密钥"
        show-password
      />
    </el-form-item>

    <el-form-item label="基础URL" v-if="formData.llm_config.provider === 'local'">
      <el-input v-model="formData.llm_config.base_url" placeholder="请输入基础URL" />
    </el-form-item>

    <!-- 工具配置 -->
    <el-divider>工具配置</el-divider>

    <div class="tools-section">
      <div class="tools-header">
        <span>可用工具</span>
        <el-button size="small" @click="addTool">
          <el-icon><Plus /></el-icon>
          添加工具
        </el-button>
      </div>

      <div v-for="(tool, index) in formData.tools" :key="index" class="tool-item">
        <el-form-item :label="`工具${index + 1}`">
          <el-space>
            <el-input v-model="tool.name" placeholder="工具名称" style="width: 120px" />
            <el-input v-model="tool.description" placeholder="工具描述" style="width: 200px" />
            <el-select v-model="tool.type" placeholder="类型" style="width: 100px">
              <el-option label="函数" value="function" />
              <el-option label="API" value="api" />
              <el-option label="数据库" value="database" />
            </el-select>
            <el-button size="small" type="danger" @click="removeTool(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-space>
        </el-form-item>
      </div>
    </div>

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
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElDivider, ElSlider, ElInputNumber, ElSpace, ElIcon } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { Agent, Tool } from '@/types/agent'

interface Props {
  agent?: Partial<Agent>
}

interface Emits {
  (e: 'submit', agent: Partial<Agent>): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()

// 表单数据
const formData = reactive<Partial<Agent>>({
  name: '',
  type: 'langgraph',
  role: '',
  goal: '',
  backstory: '',
  llm_config: {
    provider: 'openai',
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    max_tokens: 1000,
    api_key: '',
    base_url: ''
  },
  tools: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入智能体名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择智能体类型', trigger: 'change' }
  ],
  role: [
    { required: true, message: '请输入角色描述', trigger: 'blur' }
  ],
  goal: [
    { required: true, message: '请输入智能体目标', trigger: 'blur' }
  ],
  'llm_config.provider': [
    { required: true, message: '请选择LLM提供商', trigger: 'change' }
  ],
  'llm_config.model': [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ]
}

// 监听props变化
watch(() => props.agent, (newAgent) => {
  if (newAgent) {
    Object.assign(formData, newAgent)
  }
}, { immediate: true, deep: true })

// 类型变化处理
const onTypeChange = (type: string) => {
  // 根据类型设置默认配置
  switch (type) {
    case 'langgraph':
      formData.role = '分析智能体'
      formData.goal = '分析数据并提供洞察'
      formData.backstory = '我是一个专业的数据分析智能体'
      break
    case 'crewai':
      formData.role = '研究专家'
      formData.goal = '进行深度研究并提供报告'
      formData.backstory = '我是一个经验丰富的研究专家'
      break
    case 'autogen':
      formData.role = '对话助手'
      formData.goal = '与用户进行自然对话'
      formData.backstory = '我是一个友好的对话助手'
      break
  }
}

// 提供商变化处理
const onProviderChange = (provider: string) => {
  // 根据提供商设置默认模型
  switch (provider) {
    case 'openai':
      formData.llm_config!.model = 'gpt-3.5-turbo'
      break
    case 'anthropic':
      formData.llm_config!.model = 'claude-3-sonnet'
      break
    case 'local':
      formData.llm_config!.model = 'local-model'
      break
  }
}

// 工具管理
const addTool = () => {
  const newTool: Tool = {
    id: `tool_${Date.now()}`,
    name: '',
    description: '',
    type: 'function',
    config: {}
  }
  formData.tools!.push(newTool)
}

const removeTool = (index: number) => {
  formData.tools!.splice(index, 1)
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
.tools-section {
  margin-top: 16px;
}

.tools-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
  color: #303133;
}

.tool-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  background: #fafafa;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-divider) {
  margin: 20px 0 16px 0;
}
</style>
