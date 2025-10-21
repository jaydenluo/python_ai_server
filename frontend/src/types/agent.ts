/**
 * 智能体相关类型定义
 */

export interface Agent {
  id: string
  name: string
  type: AgentType
  role: string
  goal: string
  backstory: string
  llm_config: LLMConfig
  tools: Tool[]
  status: AgentStatus
  created_at: string
  updated_at: string
  performance: AgentPerformance
}

export type AgentType = 'langgraph' | 'crewai' | 'autogen'

export type AgentStatus = 'idle' | 'running' | 'busy' | 'error' | 'offline'

export interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'local'
  model: string
  temperature: number
  max_tokens: number
  api_key?: string
  base_url?: string
}

export interface Tool {
  id: string
  name: string
  description: string
  type: 'function' | 'api' | 'database'
  config: Record<string, any>
}

export interface AgentPerformance {
  total_tasks: number
  successful_tasks: number
  failed_tasks: number
  average_response_time: number
  success_rate: number
}

export interface AgentTeam {
  id: string
  name: string
  description: string
  agents: string[]
  workflow: TeamWorkflow
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

export interface TeamWorkflow {
  type: 'sequential' | 'parallel' | 'conversation'
  config: Record<string, any>
}

export interface AgentTask {
  id: string
  agent_id: string
  type: string
  input: Record<string, any>
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  result?: Record<string, any>
  error?: string
}
