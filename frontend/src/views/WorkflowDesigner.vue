<template>
  <div class="workflow-designer-page">
    <div class="page-header">
      <h1>AI工作流设计器</h1>
      <p>可视化设计和管理AI工作流程</p>
    </div>

    <div class="page-content">
      <WorkflowDesigner />
    </div>
  </div>
</template>

<script setup lang="ts">
import WorkflowDesigner from '@/components/WorkflowDesigner/WorkflowDesigner.vue'
</script>

<style scoped>
.workflow-designer-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.page-header {
  padding: 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.page-content {
  flex: 1;
  overflow: hidden;
}
</style>
