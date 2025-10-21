<template>
  <div class="autogen-node" :class="{ selected: isSelected }">
    <div class="node-header">
      <div class="node-icon">
        <el-icon><ChatDotRound /></el-icon>
      </div>
      <div class="node-type">AutoGen</div>
    </div>
    <div class="node-label">{{ data.label }}</div>
    <div class="node-description" v-if="data.description">
      {{ data.description }}
    </div>
    <div class="node-status" v-if="data.status">
      <el-tag :type="getStatusType(data.status)" size="small">
        {{ data.status }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElIcon, ElTag } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import type { NodeProps } from '@vue-flow/core'

interface Props extends NodeProps {
  data: {
    label: string
    description?: string
    status?: string
  }
}

const props = defineProps<Props>()

const isSelected = computed(() => props.selected)

const getStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'warning'
    case 'completed':
      return 'success'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}
</script>

<style scoped>
.autogen-node {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: linear-gradient(135deg, #F56C6C 0%, #F78989 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
  border: 2px solid #F56C6C;
  min-width: 160px;
  min-height: 80px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.autogen-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(245, 108, 108, 0.4);
}

.autogen-node.selected {
  border-color: #67C23A;
  box-shadow: 0 0 0 4px rgba(103, 194, 58, 0.2);
}

.node-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.node-icon {
  font-size: 20px;
  color: white;
  margin-right: 8px;
}

.node-type {
  color: white;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
}

.node-label {
  color: white;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  word-break: break-word;
}

.node-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.node-status {
  align-self: flex-start;
}
</style>
