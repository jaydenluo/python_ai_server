/**
 * 工作流相关类型定义
 */

export interface WorkflowNode {
  id: string
  type: 'start' | 'langgraph' | 'crewai' | 'autogen' | 'rag' | 'end'
  label: string
  position: { x: number; y: number }
  data: {
    agent?: string
    config?: Record<string, any>
    ragConfig?: RAGConfig
    description?: string
  }
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
  type?: 'default' | 'conditional'
  data?: Record<string, any>
}

export interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  settings: WorkflowSettings
  status: WorkflowStatus
  created_at: string
  updated_at: string
  version: number
}

export interface WorkflowSettings {
  timeout?: number
  retry_count?: number
  parallel_execution?: boolean
  error_handling?: 'stop' | 'continue' | 'retry'
}

export type WorkflowStatus = 'draft' | 'active' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'

export interface WorkflowExecution {
  id: string
  workflow_id: string
  input_data: Record<string, any>
  status: 'running' | 'completed' | 'failed' | 'paused'
  started_at: string
  completed_at?: string
  current_step: number
  steps: ExecutionStep[]
  output_data: Record<string, any>
  error?: string
}

export interface ExecutionStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  input?: Record<string, any>
  output?: Record<string, any>
  error?: string
}

export interface RAGConfig {
  knowledge_base_id: string
  top_k: number
  similarity_threshold: number
  filters?: Record<string, any>
}
