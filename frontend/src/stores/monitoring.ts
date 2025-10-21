/**
 * 监控系统状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitoringAPI } from '@/services/api'

export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: number
  active_connections: number
  timestamp: string
}

export interface Alert {
  id: string
  level: 'info' | 'warning' | 'error' | 'critical'
  title: string
  message: string
  source: string
  timestamp: string
  status: 'active' | 'resolved'
}

export interface LogEntry {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  source: string
  timestamp: string
  metadata: Record<string, any>
}

export interface Dashboard {
  id: string
  name: string
  description: string
  widgets: DashboardWidget[]
  layout: DashboardLayout
  created_at: string
  updated_at: string
}

export interface DashboardWidget {
  id: string
  type: 'chart' | 'metric' | 'table' | 'log'
  title: string
  config: Record<string, any>
  position: { x: number; y: number; w: number; h: number }
}

export interface DashboardLayout {
  columns: number
  rows: number
  gap: number
}

export const useMonitoringStore = defineStore('monitoring', () => {
  // 状态
  const metrics = ref<SystemMetrics[]>([])
  const alerts = ref<Alert[]>([])
  const logs = ref<LogEntry[]>([])
  const dashboards = ref<Dashboard[]>([])
  const currentDashboard = ref<Dashboard | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeAlerts = computed(() =>
    alerts.value.filter(alert => alert.status === 'active')
  )

  const criticalAlerts = computed(() =>
    alerts.value.filter(alert => alert.level === 'critical' && alert.status === 'active')
  )

  const recentLogs = computed(() =>
    logs.value.slice(-100) // 最近100条日志
  )

  const errorLogs = computed(() =>
    logs.value.filter(log => log.level === 'error')
  )

  const currentMetrics = computed(() =>
    metrics.value[metrics.value.length - 1] || null
  )

  // 系统指标
  const getSystemMetrics = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringAPI.getSystemMetrics()
      const newMetrics = response.data

      metrics.value.push(newMetrics)

      // 保持最近100条记录
      if (metrics.value.length > 100) {
        metrics.value = metrics.value.slice(-100)
      }

      return newMetrics
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取系统指标失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 告警管理
  const getAlerts = async (level?: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringAPI.getAlerts(level)
      alerts.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取告警失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const resolveAlert = async (alertId: string) => {
    try {
      // 这里应该调用API来解析告警
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'resolved'
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '解析告警失败'
      throw err
    }
  }

  // 日志管理
  const getLogs = async (params: Record<string, any>) => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringAPI.getLogs(params)
      logs.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取日志失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearLogs = () => {
    logs.value = []
  }

  // 仪表板管理
  const getDashboard = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringAPI.getDashboard(id)
      currentDashboard.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取仪表板失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createDashboard = async (dashboard: Record<string, any>) => {
    try {
      loading.value = true
      error.value = null

      const response = await monitoringAPI.createDashboard(dashboard)
      const newDashboard = response.data

      dashboards.value.push(newDashboard)
      return newDashboard
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建仪表板失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateDashboard = async (id: string, updates: Partial<Dashboard>) => {
    try {
      loading.value = true
      error.value = null

      // 这里应该调用API来更新仪表板
      const index = dashboards.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dashboards.value[index] = { ...dashboards.value[index], ...updates }
      }

      if (currentDashboard.value?.id === id) {
        currentDashboard.value = { ...currentDashboard.value, ...updates }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新仪表板失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDashboard = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      // 这里应该调用API来删除仪表板
      dashboards.value = dashboards.value.filter(d => d.id !== id)

      if (currentDashboard.value?.id === id) {
        currentDashboard.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除仪表板失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 实时数据更新
  const startRealTimeUpdates = () => {
    // 每5秒更新一次系统指标
    const metricsInterval = setInterval(async () => {
      try {
        await getSystemMetrics()
      } catch (error) {
        console.error('更新系统指标失败:', error)
      }
    }, 5000)

    // 每10秒更新一次告警
    const alertsInterval = setInterval(async () => {
      try {
        await getAlerts()
      } catch (error) {
        console.error('更新告警失败:', error)
      }
    }, 10000)

    // 每3秒更新一次日志
    const logsInterval = setInterval(async () => {
      try {
        await getLogs({ limit: 50 })
      } catch (error) {
        console.error('更新日志失败:', error)
      }
    }, 3000)

    return () => {
      clearInterval(metricsInterval)
      clearInterval(alertsInterval)
      clearInterval(logsInterval)
    }
  }

  // 工具方法
  const clearError = () => {
    error.value = null
  }

  const resetCurrentDashboard = () => {
    currentDashboard.value = null
  }

  return {
    // 状态
    metrics,
    alerts,
    logs,
    dashboards,
    currentDashboard,
    loading,
    error,

    // 计算属性
    activeAlerts,
    criticalAlerts,
    recentLogs,
    errorLogs,
    currentMetrics,

    // 系统指标
    getSystemMetrics,

    // 告警管理
    getAlerts,
    resolveAlert,

    // 日志管理
    getLogs,
    clearLogs,

    // 仪表板管理
    getDashboard,
    createDashboard,
    updateDashboard,
    deleteDashboard,

    // 实时更新
    startRealTimeUpdates,

    // 工具方法
    clearError,
    resetCurrentDashboard
  }
})
