<template>
  <div class="start-node" :class="{ selected: isSelected }">
    <div class="node-icon">
      <el-icon><VideoPlay /></el-icon>
    </div>
    <div class="node-label">{{ data.label }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElIcon } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import type { NodeProps } from '@vue-flow/core'

interface Props extends NodeProps {
  data: {
    label: string
  }
}

const props = defineProps<Props>()

const isSelected = computed(() => props.selected)
</script>

<style scoped>
.start-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
  border: 2px solid #67C23A;
  min-width: 120px;
  min-height: 60px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.start-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(103, 194, 58, 0.4);
}

.start-node.selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.node-icon {
  font-size: 24px;
  color: white;
  margin-bottom: 8px;
}

.node-label {
  color: white;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  word-break: break-word;
}
</style>
