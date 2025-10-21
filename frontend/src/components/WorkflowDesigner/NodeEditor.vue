<template>
  <div class="node-editor">
    <div class="header">
      <h3>节点配置</h3>
      <el-button type="text" @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <el-form :model="formData" label-width="80px" class="node-form">
      <!-- 基本信息 -->
      <el-form-item label="节点名称">
        <el-input v-model="formData.label" />
      </el-form-item>

      <el-form-item label="节点类型">
        <el-select v-model="formData.type" @change="onTypeChange">
          <el-option label="开始节点" value="start" />
          <el-option label="LangGraph" value="langgraph" />
          <el-option label="CrewAI" value="crewai" />
          <el-option label="AutoGen" value="autogen" />
          <el-option label="RAG节点" value="rag" />
          <el-option label="结束节点" value="end" />
        </el-select>
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="formData.data.description"
          type="textarea"
          :rows="2"
        />
      </el-form-item>

      <!-- LangGraph配置 -->
      <template v-if="formData.type === 'langgraph'">
        <el-divider>LangGraph配置</el-divider>

        <el-form-item label="智能体">
          <el-select v-model="formData.data.agent" placeholder="选择智能体">
            <el-option label="分析智能体" value="analyzer" />
            <el-option label="执行智能体" value="executor" />
            <el-option label="决策智能体" value="decision" />
          </el-select>
        </el-form-item>

        <el-form-item label="超时时间">
          <el-input-number
            v-model="formData.data.config.timeout"
            :min="1"
            :max="3600"
            controls-position="right"
          />
          <span class="unit">秒</span>
        </el-form-item>

        <el-form-item label="重试次数">
          <el-input-number
            v-model="formData.data.config.retryCount"
            :min="0"
            :max="5"
            controls-position="right"
          />
        </el-form-item>
      </template>

      <!-- CrewAI配置 -->
      <template v-if="formData.type === 'crewai'">
        <el-divider>CrewAI配置</el-divider>

        <el-form-item label="角色">
          <el-input v-model="formData.data.config.role" />
        </el-form-item>

        <el-form-item label="目标">
          <el-input
            v-model="formData.data.config.goal"
            type="textarea"
            :rows="2"
          />
        </el-form-item>

        <el-form-item label="背景故事">
          <el-input
            v-model="formData.data.config.backstory"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </template>

      <!-- AutoGen配置 -->
      <template v-if="formData.type === 'autogen'">
        <el-divider>AutoGen配置</el-divider>

        <el-form-item label="系统消息">
          <el-input
            v-model="formData.data.config.systemMessage"
            type="textarea"
            :rows="3"
          />
        </el-form-item>

        <el-form-item label="最大轮次">
          <el-input-number
            v-model="formData.data.config.maxTurns"
            :min="1"
            :max="10"
            controls-position="right"
          />
        </el-form-item>
      </template>

      <!-- RAG配置 -->
      <template v-if="formData.type === 'rag'">
        <el-divider>RAG配置</el-divider>

        <el-form-item label="知识库">
          <el-select v-model="formData.data.ragConfig.knowledge_base_id" placeholder="选择知识库">
            <el-option label="技术文档库" value="tech-docs" />
            <el-option label="产品手册库" value="product-manual" />
            <el-option label="FAQ库" value="faq" />
          </el-select>
        </el-form-item>

        <el-form-item label="返回数量">
          <el-input-number
            v-model="formData.data.ragConfig.top_k"
            :min="1"
            :max="20"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="相似度阈值">
          <el-slider
            v-model="formData.data.ragConfig.similarity_threshold"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
          />
        </el-form-item>
      </template>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-space>
          <el-button type="primary" @click="saveNode">保存</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="danger" @click="deleteNode">删除</el-button>
        </el-space>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElInputNumber, ElDivider, ElButton, ElSpace, ElSlider, ElIcon } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import type { WorkflowNode } from '@/types/workflow'

interface Props {
  node: WorkflowNode
}

interface Emits {
  (e: 'update', node: WorkflowNode): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 表单数据
const formData = reactive<WorkflowNode>({
  id: props.node.id,
  type: props.node.type,
  label: props.node.label,
  position: props.node.position,
  data: {
    agent: props.node.data.agent || '',
    config: props.node.data.config || {},
    ragConfig: props.node.data.ragConfig || {
      knowledge_base_id: '',
      top_k: 5,
      similarity_threshold: 0.7,
      filters: {}
    },
    description: props.node.data.description || ''
  }
})

// 监听节点变化
watch(() => props.node, (newNode) => {
  Object.assign(formData, newNode)
}, { deep: true })

// 类型变化处理
const onTypeChange = (type: string) => {
  // 根据类型初始化配置
  switch (type) {
    case 'langgraph':
      formData.data.config = {
        timeout: 30,
        retryCount: 3,
        ...formData.data.config
      }
      break
    case 'crewai':
      formData.data.config = {
        role: '',
        goal: '',
        backstory: '',
        ...formData.data.config
      }
      break
    case 'autogen':
      formData.data.config = {
        systemMessage: '',
        maxTurns: 3,
        ...formData.data.config
      }
      break
    case 'rag':
      formData.data.ragConfig = {
        knowledge_base_id: '',
        top_k: 5,
        similarity_threshold: 0.7,
        filters: {},
        ...formData.data.ragConfig
      }
      break
  }
}

// 保存节点
const saveNode = () => {
  emit('update', { ...formData })
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, props.node)
}

// 删除节点
const deleteNode = () => {
  // 这里应该触发删除事件，由父组件处理
  console.log('删除节点:', formData.id)
}
</script>

<style scoped>
.node-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.node-form {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.unit {
  margin-left: 8px;
  color: #666;
  font-size: 12px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-divider) {
  margin: 20px 0 16px 0;
}
</style>
