/**
 * API服务
 */

import axios from 'axios'
import type { Workflow, WorkflowExecution } from '@/types/workflow'
import type { Agent, AgentTeam } from '@/types/agent'
import type { KnowledgeBase, Document, RAGQuery } from '@/types/rag'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // 处理认证失败
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 工作流API
export const workflowAPI = {
  // 创建工作流
  createWorkflow: (workflow: Partial<Workflow>) =>
    api.post('/workflows', workflow),

  // 获取工作流
  getWorkflow: (id: string) =>
    api.get(`/workflows/${id}`),

  // 更新工作流
  updateWorkflow: (id: string, updates: Partial<Workflow>) =>
    api.put(`/workflows/${id}`, updates),

  // 删除工作流
  deleteWorkflow: (id: string) =>
    api.delete(`/workflows/${id}`),

  // 获取工作流列表
  listWorkflows: () =>
    api.get('/workflows'),

  // 执行工作流
  executeWorkflow: (id: string, inputData: Record<string, any>) =>
    api.post(`/workflows/${id}/execute`, inputData),

  // 获取执行状态
  getExecutionStatus: (executionId: string) =>
    api.get(`/executions/${executionId}`),

  // 暂停工作流
  pauseWorkflow: (id: string) =>
    api.post(`/workflows/${id}/pause`),

  // 恢复工作流
  resumeWorkflow: (id: string) =>
    api.post(`/workflows/${id}/resume`)
}

// 智能体API
export const agentAPI = {
  // 创建智能体
  createAgent: (agent: Partial<Agent>) =>
    api.post('/agents', agent),

  // 获取智能体
  getAgent: (id: string) =>
    api.get(`/agents/${id}`),

  // 更新智能体
  updateAgent: (id: string, updates: Partial<Agent>) =>
    api.put(`/agents/${id}`, updates),

  // 删除智能体
  deleteAgent: (id: string) =>
    api.delete(`/agents/${id}`),

  // 获取智能体列表
  listAgents: (type?: string) =>
    api.get('/agents', { params: { type } }),

  // 执行智能体任务
  executeTask: (id: string, task: Record<string, any>) =>
    api.post(`/agents/${id}/execute`, task),

  // 创建团队
  createTeam: (team: Partial<AgentTeam>) =>
    api.post('/teams', team),

  // 获取团队
  getTeam: (id: string) =>
    api.get(`/teams/${id}`),

  // 更新团队
  updateTeam: (id: string, updates: Partial<AgentTeam>) =>
    api.put(`/teams/${id}`, updates),

  // 删除团队
  deleteTeam: (id: string) =>
    api.delete(`/teams/${id}`),

  // 获取团队列表
  listTeams: () =>
    api.get('/teams'),

  // 执行团队任务
  executeTeamTask: (id: string, task: Record<string, any>) =>
    api.post(`/teams/${id}/execute`, task)
}

// RAG API
export const ragAPI = {
  // 创建知识库
  createKnowledgeBase: (kb: Partial<KnowledgeBase>) =>
    api.post('/knowledge-bases', kb),

  // 获取知识库
  getKnowledgeBase: (id: string) =>
    api.get(`/knowledge-bases/${id}`),

  // 更新知识库
  updateKnowledgeBase: (id: string, updates: Partial<KnowledgeBase>) =>
    api.put(`/knowledge-bases/${id}`, updates),

  // 删除知识库
  deleteKnowledgeBase: (id: string) =>
    api.delete(`/knowledge-bases/${id}`),

  // 获取知识库列表
  listKnowledgeBases: () =>
    api.get('/knowledge-bases'),

  // 上传文档
  uploadDocuments: (kbId: string, documents: Document[]) =>
    api.post(`/knowledge-bases/${kbId}/documents`, { documents }),

  // 搜索文档
  searchDocuments: (query: RAGQuery) =>
    api.post('/search', query),

  // 删除文档
  deleteDocuments: (kbId: string, documentIds: string[]) =>
    api.delete(`/knowledge-bases/${kbId}/documents`, { data: { documentIds } }),

  // 获取知识库统计
  getKnowledgeBaseStats: (id: string) =>
    api.get(`/knowledge-bases/${id}/stats`)
}

// 监控API
export const monitoringAPI = {
  // 获取系统指标
  getSystemMetrics: () =>
    api.get('/monitoring/metrics'),

  // 获取告警列表
  getAlerts: (level?: string) =>
    api.get('/monitoring/alerts', { params: { level } }),

  // 获取日志
  getLogs: (params: Record<string, any>) =>
    api.get('/monitoring/logs', { params }),

  // 获取仪表板
  getDashboard: (id: string) =>
    api.get(`/monitoring/dashboards/${id}`),

  // 创建仪表板
  createDashboard: (dashboard: Record<string, any>) =>
    api.post('/monitoring/dashboards', dashboard)
}

// WebSocket连接
export class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect() {
    const wsUrl = `ws://localhost:8000/ws`
    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.log('WebSocket连接已建立')
      this.reconnectAttempts = 0
    }

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleMessage(data)
    }

    this.socket.onclose = () => {
      console.log('WebSocket连接已关闭')
      this.reconnect()
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  send(message: Record<string, any>) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => this.connect(), 5000)
    }
  }

  private handleMessage(data: any) {
    // 处理不同类型的消息
    switch (data.type) {
      case 'workflow_status':
        // 处理工作流状态更新
        break
      case 'agent_status':
        // 处理智能体状态更新
        break
      case 'execution_progress':
        // 处理执行进度更新
        break
      case 'alert':
        // 处理告警消息
        break
      default:
        console.log('未知消息类型:', data.type)
    }
  }
}

export default api
