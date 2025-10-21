<template>
  <div class="workflow-designer">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-space>
        <el-button type="primary" @click="addNode">
          <el-icon><Plus /></el-icon>
          添加节点
        </el-button>
        <el-button type="success" @click="addEdge">
          <el-icon><Connection /></el-icon>
          连接节点
        </el-button>
        <el-button type="warning" @click="saveWorkflow">
          <el-icon><Document /></el-icon>
          保存工作流
        </el-button>
        <el-button type="info" @click="executeWorkflow">
          <el-icon><VideoPlay /></el-icon>
          执行工作流
        </el-button>
      </el-space>
    </div>

    <!-- 工作流画布 -->
    <div class="canvas-container">
      <VueFlow
        :nodes="nodes"
        :edges="edges"
        @node-click="onNodeClick"
        @edge-click="onEdgeClick"
        @connect="onConnect"
        class="workflow-canvas"
      >
        <Background />
        <Controls />
        <MiniMap />

        <!-- 自定义节点 -->
        <template #node-start="nodeProps">
          <StartNode v-bind="nodeProps" />
        </template>

        <template #node-langgraph="nodeProps">
          <LangGraphNode v-bind="nodeProps" />
        </template>

        <template #node-crewai="nodeProps">
          <CrewAINode v-bind="nodeProps" />
        </template>

        <template #node-autogen="nodeProps">
          <AutoGenNode v-bind="nodeProps" />
        </template>

        <template #node-rag="nodeProps">
          <RAGNode v-bind="nodeProps" />
        </template>

        <template #node-end="nodeProps">
          <EndNode v-bind="nodeProps" />
        </template>
      </VueFlow>
    </div>

    <!-- 属性面板 -->
    <div class="properties-panel" v-if="selectedNode">
      <NodeEditor
        :node="selectedNode"
        @update="updateNode"
        @close="closeNodeEditor"
      />
    </div>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="showExecutionDialog"
      title="执行工作流"
      width="500px"
    >
      <el-form :model="executionForm" label-width="100px">
        <el-form-item label="输入数据">
          <el-input
            v-model="executionForm.inputData"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的输入数据"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showExecutionDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute">确认执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { ElButton, ElSpace, ElIcon, ElDialog, ElForm, ElFormItem, ElInput, ElMessage } from 'element-plus'
import { Plus, Connection, Document, VideoPlay } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { WorkflowNode, WorkflowEdge } from '@/types/workflow'

// 导入自定义节点组件
import StartNode from './nodes/StartNode.vue'
import LangGraphNode from './nodes/LangGraphNode.vue'
import CrewAINode from './nodes/CrewAINode.vue'
import AutoGenNode from './nodes/AutoGenNode.vue'
import RAGNode from './nodes/RAGNode.vue'
import EndNode from './nodes/EndNode.vue'
import NodeEditor from './NodeEditor.vue'

const workflowStore = useWorkflowStore()

// 状态
const nodes = ref<WorkflowNode[]>([])
const edges = ref<WorkflowEdge[]>([])
const selectedNode = ref<WorkflowNode | null>(null)
const showExecutionDialog = ref(false)
const executionForm = ref({
  inputData: '{}'
})

// 计算属性
const currentWorkflow = computed(() => workflowStore.currentWorkflow)

// 生命周期
onMounted(() => {
  if (currentWorkflow.value) {
    nodes.value = currentWorkflow.value.nodes
    edges.value = currentWorkflow.value.edges
  }
})

// 节点管理
const addNode = () => {
  const newNode: WorkflowNode = {
    id: `node_${Date.now()}`,
    type: 'langgraph',
    label: '新节点',
    position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
    data: {
      description: '',
      config: {}
    }
  }

  nodes.value.push(newNode)
  workflowStore.addNode(newNode)
}

const updateNode = (nodeId: string, updates: Partial<WorkflowNode>) => {
  const index = nodes.value.findIndex(n => n.id === nodeId)
  if (index !== -1) {
    nodes.value[index] = { ...nodes.value[index], ...updates }
    workflowStore.updateNode(nodeId, updates)
  }
}

const removeNode = (nodeId: string) => {
  nodes.value = nodes.value.filter(n => n.id !== nodeId)
  edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
  workflowStore.removeNode(nodeId)
}

// 边管理
const addEdge = () => {
  // 实现边添加逻辑
  console.log('添加边')
}

const onConnect = (connection: any) => {
  const newEdge: WorkflowEdge = {
    id: `edge_${Date.now()}`,
    source: connection.source,
    target: connection.target,
    type: 'default'
  }

  edges.value.push(newEdge)
  workflowStore.addEdge(newEdge)
}

// 事件处理
const onNodeClick = (event: any, node: WorkflowNode) => {
  selectedNode.value = node
}

const onEdgeClick = (event: any, edge: WorkflowEdge) => {
  console.log('边被点击:', edge)
}

const closeNodeEditor = () => {
  selectedNode.value = null
}

// 工作流操作
const saveWorkflow = async () => {
  try {
    if (currentWorkflow.value) {
      await workflowStore.updateWorkflow(currentWorkflow.value.id, {
        nodes: nodes.value,
        edges: edges.value
      })
      ElMessage.success('工作流保存成功')
    } else {
      const newWorkflow = await workflowStore.createWorkflow({
        name: '新工作流',
        description: '',
        nodes: nodes.value,
        edges: edges.value,
        settings: {}
      })
      ElMessage.success('工作流创建成功')
    }
  } catch (error) {
    ElMessage.error('保存工作流失败')
  }
}

const executeWorkflow = () => {
  if (!currentWorkflow.value) {
    ElMessage.warning('请先保存工作流')
    return
  }
  showExecutionDialog.value = true
}

const confirmExecute = async () => {
  try {
    const inputData = JSON.parse(executionForm.value.inputData)
    await workflowStore.executeWorkflow(currentWorkflow.value!.id, inputData)
    ElMessage.success('工作流执行已开始')
    showExecutionDialog.value = false
  } catch (error) {
    ElMessage.error('执行工作流失败')
  }
}
</script>

<style scoped>
.workflow-designer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.toolbar {
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #fafafa;
}

.workflow-canvas {
  width: 100%;
  height: 100%;
}

.properties-panel {
  position: absolute;
  right: 0;
  top: 0;
  width: 300px;
  height: 100%;
  background: white;
  border-left: 1px solid #e0e0e0;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}
</style>
