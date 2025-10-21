/**
 * 工作流状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution } from '@/types/workflow'
import { workflowAPI } from '@/services/api'

export const useWorkflowStore = defineStore('workflow', () => {
  // 状态
  const workflows = ref<Workflow[]>([])
  const currentWorkflow = ref<Workflow | null>(null)
  const executions = ref<WorkflowExecution[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeWorkflows = computed(() =>
    workflows.value.filter(w => w.status === 'active')
  )

  const runningExecutions = computed(() =>
    executions.value.filter(e => e.status === 'running')
  )

  // 工作流管理
  const createWorkflow = async (workflowConfig: Partial<Workflow>) => {
    try {
      loading.value = true
      error.value = null

      const response = await workflowAPI.createWorkflow(workflowConfig)
      const newWorkflow = response.data

      workflows.value.push(newWorkflow)
      return newWorkflow
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建工作流失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getWorkflow = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await workflowAPI.getWorkflow(id)
      currentWorkflow.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取工作流失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateWorkflow = async (id: string, updates: Partial<Workflow>) => {
    try {
      loading.value = true
      error.value = null

      const response = await workflowAPI.updateWorkflow(id, updates)
      const updatedWorkflow = response.data

      const index = workflows.value.findIndex(w => w.id === id)
      if (index !== -1) {
        workflows.value[index] = updatedWorkflow
      }

      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = updatedWorkflow
      }

      return updatedWorkflow
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新工作流失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteWorkflow = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      await workflowAPI.deleteWorkflow(id)

      workflows.value = workflows.value.filter(w => w.id !== id)

      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除工作流失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const listWorkflows = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await workflowAPI.listWorkflows()
      workflows.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取工作流列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 工作流执行
  const executeWorkflow = async (id: string, inputData: Record<string, any>) => {
    try {
      loading.value = true
      error.value = null

      const response = await workflowAPI.executeWorkflow(id, inputData)
      const execution = response.data

      executions.value.push(execution)
      return execution
    } catch (err) {
      error.value = err instanceof Error ? err.message : '执行工作流失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getExecutionStatus = async (executionId: string) => {
    try {
      const response = await workflowAPI.getExecutionStatus(executionId)
      const execution = response.data

      const index = executions.value.findIndex(e => e.id === executionId)
      if (index !== -1) {
        executions.value[index] = execution
      } else {
        executions.value.push(execution)
      }

      return execution
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取执行状态失败'
      throw err
    }
  }

  const pauseWorkflow = async (id: string) => {
    try {
      await workflowAPI.pauseWorkflow(id)

      const workflow = workflows.value.find(w => w.id === id)
      if (workflow) {
        workflow.status = 'paused'
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '暂停工作流失败'
      throw err
    }
  }

  const resumeWorkflow = async (id: string) => {
    try {
      await workflowAPI.resumeWorkflow(id)

      const workflow = workflows.value.find(w => w.id === id)
      if (workflow) {
        workflow.status = 'active'
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '恢复工作流失败'
      throw err
    }
  }

  // 节点管理
  const addNode = (node: WorkflowNode) => {
    if (currentWorkflow.value) {
      currentWorkflow.value.nodes.push(node)
    }
  }

  const updateNode = (nodeId: string, updates: Partial<WorkflowNode>) => {
    if (currentWorkflow.value) {
      const index = currentWorkflow.value.nodes.findIndex(n => n.id === nodeId)
      if (index !== -1) {
        currentWorkflow.value.nodes[index] = { ...currentWorkflow.value.nodes[index], ...updates }
      }
    }
  }

  const removeNode = (nodeId: string) => {
    if (currentWorkflow.value) {
      currentWorkflow.value.nodes = currentWorkflow.value.nodes.filter(n => n.id !== nodeId)
      currentWorkflow.value.edges = currentWorkflow.value.edges.filter(
        e => e.source !== nodeId && e.target !== nodeId
      )
    }
  }

  // 边管理
  const addEdge = (edge: WorkflowEdge) => {
    if (currentWorkflow.value) {
      currentWorkflow.value.edges.push(edge)
    }
  }

  const updateEdge = (edgeId: string, updates: Partial<WorkflowEdge>) => {
    if (currentWorkflow.value) {
      const index = currentWorkflow.value.edges.findIndex(e => e.id === edgeId)
      if (index !== -1) {
        currentWorkflow.value.edges[index] = { ...currentWorkflow.value.edges[index], ...updates }
      }
    }
  }

  const removeEdge = (edgeId: string) => {
    if (currentWorkflow.value) {
      currentWorkflow.value.edges = currentWorkflow.value.edges.filter(e => e.id !== edgeId)
    }
  }

  // 清理状态
  const clearError = () => {
    error.value = null
  }

  const resetCurrentWorkflow = () => {
    currentWorkflow.value = null
  }

  return {
    // 状态
    workflows,
    currentWorkflow,
    executions,
    loading,
    error,

    // 计算属性
    activeWorkflows,
    runningExecutions,

    // 工作流管理
    createWorkflow,
    getWorkflow,
    updateWorkflow,
    deleteWorkflow,
    listWorkflows,

    // 工作流执行
    executeWorkflow,
    getExecutionStatus,
    pauseWorkflow,
    resumeWorkflow,

    // 节点管理
    addNode,
    updateNode,
    removeNode,

    // 边管理
    addEdge,
    updateEdge,
    removeEdge,

    // 工具方法
    clearError,
    resetCurrentWorkflow
  }
})
