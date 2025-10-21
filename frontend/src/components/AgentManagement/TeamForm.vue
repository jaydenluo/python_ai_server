<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
    <!-- 基本信息 -->
    <el-form-item label="团队名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入团队名称" />
    </el-form-item>

    <el-form-item label="团队描述" prop="description">
      <el-input
        v-model="formData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入团队描述"
      />
    </el-form-item>

    <!-- 智能体选择 -->
    <el-divider>智能体配置</el-divider>

    <el-form-item label="选择智能体" prop="agents">
      <el-select
        v-model="formData.agents"
        multiple
        placeholder="请选择智能体"
        style="width: 100%"
      >
        <el-option
          v-for="agent in availableAgents"
          :key="agent.id"
          :label="`${agent.name} (${getAgentTypeName(agent.type)})`"
          :value="agent.id"
        />
      </el-select>
    </el-form-item>

    <!-- 工作流配置 -->
    <el-divider>工作流配置</el-divider>

    <el-form-item label="工作流类型" prop="workflow.type">
      <el-select v-model="formData.workflow.type" @change="onWorkflowTypeChange">
        <el-option label="顺序执行" value="sequential" />
        <el-option label="并行执行" value="parallel" />
        <el-option label="对话式" value="conversation" />
      </el-select>
    </el-form-item>

    <!-- 顺序执行配置 -->
    <template v-if="formData.workflow.type === 'sequential'">
      <el-form-item label="执行顺序">
        <div class="agent-order">
          <div
            v-for="(agentId, index) in formData.agents"
            :key="agentId"
            class="order-item"
          >
            <span class="order-number">{{ index + 1 }}</span>
            <span class="agent-name">{{ getAgentName(agentId) }}</span>
            <el-button
              size="small"
              type="danger"
              @click="removeAgentFromOrder(agentId)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </el-form-item>
    </template>

    <!-- 并行执行配置 -->
    <template v-if="formData.workflow.type === 'parallel'">
      <el-form-item label="并发数量">
        <el-input-number
          v-model="formData.workflow.config.maxConcurrency"
          :min="1"
          :max="10"
          controls-position="right"
        />
        <span class="form-tip">同时执行的最大智能体数量</span>
      </el-form-item>
    </template>

    <!-- 对话式配置 -->
    <template v-if="formData.workflow.type === 'conversation'">
      <el-form-item label="最大轮次">
        <el-input-number
          v-model="formData.workflow.config.maxTurns"
          :min="1"
          :max="20"
          controls-position="right"
        />
        <span class="form-tip">智能体之间的最大对话轮次</span>
      </el-form-item>

      <el-form-item label="对话主题">
        <el-input
          v-model="formData.workflow.config.topic"
          placeholder="请输入对话主题"
        />
      </el-form-item>
    </template>

    <!-- 高级配置 -->
    <el-divider>高级配置</el-divider>

    <el-form-item label="超时时间">
      <el-input-number
        v-model="formData.workflow.config.timeout"
        :min="1"
        :max="3600"
        controls-position="right"
      />
      <span class="form-tip">秒</span>
    </el-form-item>

    <el-form-item label="重试次数">
      <el-input-number
        v-model="formData.workflow.config.retryCount"
        :min="0"
        :max="5"
        controls-position="right"
      />
    </el-form-item>

    <el-form-item label="错误处理">
      <el-select v-model="formData.workflow.config.errorHandling">
        <el-option label="停止执行" value="stop" />
        <el-option label="继续执行" value="continue" />
        <el-option label="重试执行" value="retry" />
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
import { ref, reactive, computed, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElDivider, ElInputNumber, ElSpace, ElIcon } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import type { AgentTeam, Agent } from '@/types/agent'

interface Props {
  team?: Partial<AgentTeam>
  agents: Agent[]
}

interface Emits {
  (e: 'submit', team: Partial<AgentTeam>): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()

// 表单数据
const formData = reactive<Partial<AgentTeam>>({
  name: '',
  description: '',
  agents: [],
  workflow: {
    type: 'sequential',
    config: {
      maxConcurrency: 3,
      maxTurns: 5,
      topic: '',
      timeout: 300,
      retryCount: 2,
      errorHandling: 'stop'
    }
  },
  status: 'active'
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入团队名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入团队描述', trigger: 'blur' }
  ],
  agents: [
    { required: true, message: '请选择至少一个智能体', trigger: 'change' }
  ],
  'workflow.type': [
    { required: true, message: '请选择工作流类型', trigger: 'change' }
  ]
}

// 计算属性
const availableAgents = computed(() => props.agents)

// 监听props变化
watch(() => props.team, (newTeam) => {
  if (newTeam) {
    Object.assign(formData, newTeam)
  }
}, { immediate: true, deep: true })

// 工作流类型变化处理
const onWorkflowTypeChange = (type: string) => {
  // 根据类型重置配置
  formData.workflow!.config = {
    maxConcurrency: 3,
    maxTurns: 5,
    topic: '',
    timeout: 300,
    retryCount: 2,
    errorHandling: 'stop'
  }
}

// 工具方法
const getAgentName = (agentId: string) => {
  const agent = props.agents.find(a => a.id === agentId)
  return agent ? agent.name : '未知智能体'
}

const getAgentTypeName = (type: string) => {
  switch (type) {
    case 'langgraph': return 'LangGraph'
    case 'crewai': return 'CrewAI'
    case 'autogen': return 'AutoGen'
    default: return '未知'
  }
}

const removeAgentFromOrder = (agentId: string) => {
  const index = formData.agents!.indexOf(agentId)
  if (index > -1) {
    formData.agents!.splice(index, 1)
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
.agent-order {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.order-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.agent-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

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
