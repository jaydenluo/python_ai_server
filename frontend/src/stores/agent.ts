/**
 * 智能体状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Agent, AgentTeam, AgentTask } from '@/types/agent'
import { agentAPI } from '@/services/api'

export const useAgentStore = defineStore('agent', () => {
  // 状态
  const agents = ref<Agent[]>([])
  const teams = ref<AgentTeam[]>([])
  const tasks = ref<AgentTask[]>([])
  const currentAgent = ref<Agent | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const langgraphAgents = computed(() =>
    agents.value.filter(a => a.type === 'langgraph')
  )

  const crewaiAgents = computed(() =>
    agents.value.filter(a => a.type === 'crewai')
  )

  const autogenAgents = computed(() =>
    agents.value.filter(a => a.type === 'autogen')
  )

  const activeAgents = computed(() =>
    agents.value.filter(a => a.status === 'idle' || a.status === 'running')
  )

  const runningTasks = computed(() =>
    tasks.value.filter(t => t.status === 'running')
  )

  // 智能体管理
  const createAgent = async (agentConfig: Partial<Agent>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.createAgent(agentConfig)
      const newAgent = response.data

      agents.value.push(newAgent)
      return newAgent
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建智能体失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAgent = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.getAgent(id)
      currentAgent.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取智能体失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAgent = async (id: string, updates: Partial<Agent>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.updateAgent(id, updates)
      const updatedAgent = response.data

      const index = agents.value.findIndex(a => a.id === id)
      if (index !== -1) {
        agents.value[index] = updatedAgent
      }

      if (currentAgent.value?.id === id) {
        currentAgent.value = updatedAgent
      }

      return updatedAgent
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新智能体失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteAgent = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      await agentAPI.deleteAgent(id)

      agents.value = agents.value.filter(a => a.id !== id)

      if (currentAgent.value?.id === id) {
        currentAgent.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除智能体失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const listAgents = async (type?: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.listAgents(type)
      agents.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取智能体列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 智能体执行
  const executeTask = async (agentId: string, task: Record<string, any>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.executeTask(agentId, task)
      const newTask = response.data

      tasks.value.push(newTask)
      return newTask
    } catch (err) {
      error.value = err instanceof Error ? err.message : '执行任务失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getTaskStatus = async (taskId: string) => {
    try {
      const response = await agentAPI.getTaskStatus(taskId)
      const task = response.data

      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      } else {
        tasks.value.push(task)
      }

      return task
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取任务状态失败'
      throw err
    }
  }

  // 团队管理
  const createTeam = async (teamConfig: Partial<AgentTeam>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.createTeam(teamConfig)
      const newTeam = response.data

      teams.value.push(newTeam)
      return newTeam
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建团队失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getTeam = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.getTeam(id)
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取团队失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTeam = async (id: string, updates: Partial<AgentTeam>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.updateTeam(id, updates)
      const updatedTeam = response.data

      const index = teams.value.findIndex(t => t.id === id)
      if (index !== -1) {
        teams.value[index] = updatedTeam
      }

      return updatedTeam
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新团队失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTeam = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      await agentAPI.deleteTeam(id)

      teams.value = teams.value.filter(t => t.id !== id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除团队失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const listTeams = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.listTeams()
      teams.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取团队列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 团队执行
  const executeTeamTask = async (teamId: string, task: Record<string, any>) => {
    try {
      loading.value = true
      error.value = null

      const response = await agentAPI.executeTeamTask(teamId, task)
      const newTask = response.data

      tasks.value.push(newTask)
      return newTask
    } catch (err) {
      error.value = err instanceof Error ? err.message : '执行团队任务失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 工具方法
  const clearError = () => {
    error.value = null
  }

  const resetCurrentAgent = () => {
    currentAgent.value = null
  }

  return {
    // 状态
    agents,
    teams,
    tasks,
    currentAgent,
    loading,
    error,

    // 计算属性
    langgraphAgents,
    crewaiAgents,
    autogenAgents,
    activeAgents,
    runningTasks,

    // 智能体管理
    createAgent,
    getAgent,
    updateAgent,
    deleteAgent,
    listAgents,

    // 智能体执行
    executeTask,
    getTaskStatus,

    // 团队管理
    createTeam,
    getTeam,
    updateTeam,
    deleteTeam,
    listTeams,

    // 团队执行
    executeTeamTask,

    // 工具方法
    clearError,
    resetCurrentAgent
  }
})
