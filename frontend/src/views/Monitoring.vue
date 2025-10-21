<template>
  <div class="monitoring">
    <div class="page-header">
      <h1>监控中心</h1>
      <p>实时监控系统状态和性能指标</p>

      <div class="header-actions">
        <el-button type="primary" @click="showCreateDashboardDialog = true">
          <el-icon><Plus /></el-icon>
          创建仪表板
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <div class="content">
      <!-- 系统概览 -->
      <div class="overview-section">
        <div class="section-header">
          <h2>系统概览</h2>
          <el-tag :type="getSystemStatusType()">
            {{ getSystemStatus() }}
          </el-tag>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">CPU使用率</span>
              <el-icon class="metric-icon"><Monitor /></el-icon>
            </div>
            <div class="metric-value">{{ currentMetrics?.cpu_usage || 0 }}%</div>
            <div class="metric-chart">
              <el-progress
                :percentage="currentMetrics?.cpu_usage || 0"
                :color="getProgressColor(currentMetrics?.cpu_usage || 0)"
              />
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">内存使用率</span>
              <el-icon class="metric-icon"><Monitor /></el-icon>
            </div>
            <div class="metric-value">{{ currentMetrics?.memory_usage || 0 }}%</div>
            <div class="metric-chart">
              <el-progress
                :percentage="currentMetrics?.memory_usage || 0"
                :color="getProgressColor(currentMetrics?.memory_usage || 0)"
              />
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">磁盘使用率</span>
              <el-icon class="metric-icon"><Monitor /></el-icon>
            </div>
            <div class="metric-value">{{ currentMetrics?.disk_usage || 0 }}%</div>
            <div class="metric-chart">
              <el-progress
                :percentage="currentMetrics?.disk_usage || 0"
                :color="getProgressColor(currentMetrics?.disk_usage || 0)"
              />
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">活跃连接</span>
              <el-icon class="metric-icon"><Connection /></el-icon>
            </div>
            <div class="metric-value">{{ currentMetrics?.active_connections || 0 }}</div>
            <div class="metric-trend">
              <el-icon class="trend-icon"><TrendCharts /></el-icon>
              <span class="trend-text">+12%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 告警中心 -->
      <div class="alerts-section">
        <div class="section-header">
          <h2>告警中心</h2>
          <el-space>
            <el-select v-model="alertFilter" placeholder="筛选告警" @change="filterAlerts">
              <el-option label="全部" value="" />
              <el-option label="严重" value="critical" />
              <el-option label="错误" value="error" />
              <el-option label="警告" value="warning" />
              <el-option label="信息" value="info" />
            </el-select>
            <el-button @click="refreshAlerts">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
        </div>

        <div class="alerts-list">
          <div
            v-for="alert in filteredAlerts"
            :key="alert.id"
            class="alert-item"
            :class="`alert-${alert.level}`"
          >
            <div class="alert-header">
              <div class="alert-level">
                <el-icon>
                  <component :is="getAlertIcon(alert.level)" />
                </el-icon>
                <span>{{ getAlertLevelName(alert.level) }}</span>
              </div>
              <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
            </div>

            <div class="alert-content">
              <h4>{{ alert.title }}</h4>
              <p>{{ alert.message }}</p>
            </div>

            <div class="alert-footer">
              <span class="alert-source">{{ alert.source }}</span>
              <el-button
                size="small"
                type="primary"
                @click="resolveAlert(alert.id)"
                v-if="alert.status === 'active'"
              >
                解析
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 日志中心 -->
      <div class="logs-section">
        <div class="section-header">
          <h2>日志中心</h2>
          <el-space>
            <el-select v-model="logFilter" placeholder="筛选日志" @change="filterLogs">
              <el-option label="全部" value="" />
              <el-option label="错误" value="error" />
              <el-option label="警告" value="warning" />
              <el-option label="信息" value="info" />
              <el-option label="调试" value="debug" />
            </el-select>
            <el-button @click="refreshLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </el-space>
        </div>

        <div class="logs-list">
          <div
            v-for="log in filteredLogs"
            :key="log.id"
            class="log-item"
            :class="`log-${log.level}`"
          >
            <div class="log-header">
              <div class="log-level">
                <el-icon>
                  <component :is="getLogIcon(log.level)" />
                </el-icon>
                <span>{{ getLogLevelName(log.level) }}</span>
              </div>
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            </div>

            <div class="log-content">
              <span class="log-message">{{ log.message }}</span>
              <span class="log-source">{{ log.source }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 仪表板列表 -->
      <div class="dashboards-section">
        <div class="section-header">
          <h2>仪表板</h2>
          <el-button @click="refreshDashboards">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div class="dashboards-grid">
          <div
            v-for="dashboard in dashboards"
            :key="dashboard.id"
            class="dashboard-card"
            @click="openDashboard(dashboard)"
          >
            <div class="dashboard-header">
              <h3>{{ dashboard.name }}</h3>
              <el-button size="small" type="danger" @click.stop="deleteDashboard(dashboard.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>

            <p class="dashboard-description">{{ dashboard.description }}</p>

            <div class="dashboard-stats">
              <span class="stat">{{ dashboard.widgets.length }} 个组件</span>
              <span class="stat">{{ formatDate(dashboard.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建仪表板对话框 -->
    <el-dialog
      v-model="showCreateDashboardDialog"
      title="创建仪表板"
      width="500px"
    >
      <DashboardForm
        :dashboard="newDashboard"
        @submit="createDashboard"
        @cancel="showCreateDashboardDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElButton, ElIcon, ElSpace, ElSelect, ElOption, ElTag, ElProgress, ElDialog, ElMessage } from 'element-plus'
import { Plus, Refresh, Delete, Monitor, Connection, TrendCharts, Warning, CircleCheck, CircleClose, InfoFilled } from '@element-plus/icons-vue'
import { useMonitoringStore } from '@/stores/monitoring'
import type { Alert, LogEntry, Dashboard } from '@/stores/monitoring'
import DashboardForm from '@/components/Monitoring/DashboardForm.vue'

const monitoringStore = useMonitoringStore()

// 状态
const alertFilter = ref('')
const logFilter = ref('')
const showCreateDashboardDialog = ref(false)
const newDashboard = ref<Partial<Dashboard>>({})
let stopRealTimeUpdates: (() => void) | null = null

// 计算属性
const currentMetrics = computed(() => monitoringStore.currentMetrics)
const alerts = computed(() => monitoringStore.alerts)
const logs = computed(() => monitoringStore.logs)
const dashboards = computed(() => monitoringStore.dashboards)
const loading = computed(() => monitoringStore.loading)

const filteredAlerts = computed(() => {
  if (!alertFilter.value) return alerts.value
  return alerts.value.filter(alert => alert.level === alertFilter.value)
})

const filteredLogs = computed(() => {
  if (!logFilter.value) return logs.value
  return logs.value.filter(log => log.level === logFilter.value)
})

// 生命周期
onMounted(() => {
  loadData()
  startRealTimeUpdates()
})

onUnmounted(() => {
  if (stopRealTimeUpdates) {
    stopRealTimeUpdates()
  }
})

// 数据加载
const loadData = async () => {
  try {
    await Promise.all([
      monitoringStore.getSystemMetrics(),
      monitoringStore.getAlerts(),
      monitoringStore.getLogs({ limit: 100 }),
      monitoringStore.getDashboards()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const refreshData = () => {
  loadData()
}

const refreshAlerts = () => {
  monitoringStore.getAlerts()
}

const refreshLogs = () => {
  monitoringStore.getLogs({ limit: 100 })
}

const refreshDashboards = () => {
  monitoringStore.getDashboards()
}

const startRealTimeUpdates = () => {
  stopRealTimeUpdates = monitoringStore.startRealTimeUpdates()
}

// 告警操作
const resolveAlert = async (alertId: string) => {
  try {
    await monitoringStore.resolveAlert(alertId)
    ElMessage.success('告警已解析')
  } catch (error) {
    ElMessage.error('解析告警失败')
  }
}

const filterAlerts = () => {
  // 筛选逻辑已在计算属性中处理
}

// 日志操作
const clearLogs = () => {
  monitoringStore.clearLogs()
  ElMessage.success('日志已清空')
}

const filterLogs = () => {
  // 筛选逻辑已在计算属性中处理
}

// 仪表板操作
const openDashboard = (dashboard: Dashboard) => {
  // 实现打开仪表板逻辑
  console.log('打开仪表板:', dashboard)
}

const deleteDashboard = async (id: string) => {
  try {
    await monitoringStore.deleteDashboard(id)
    ElMessage.success('仪表板删除成功')
  } catch (error) {
    ElMessage.error('删除仪表板失败')
  }
}

const createDashboard = async (dashboardData: Partial<Dashboard>) => {
  try {
    await monitoringStore.createDashboard(dashboardData)
    showCreateDashboardDialog.value = false
    newDashboard.value = {}
    ElMessage.success('仪表板创建成功')
  } catch (error) {
    ElMessage.error('创建仪表板失败')
  }
}

// 工具方法
const getSystemStatus = () => {
  if (!currentMetrics.value) return '未知'

  const cpu = currentMetrics.value.cpu_usage
  const memory = currentMetrics.value.memory_usage

  if (cpu > 90 || memory > 90) return '严重'
  if (cpu > 70 || memory > 70) return '警告'
  return '正常'
}

const getSystemStatusType = () => {
  const status = getSystemStatus()
  switch (status) {
    case '严重': return 'danger'
    case '警告': return 'warning'
    case '正常': return 'success'
    default: return 'info'
  }
}

const getProgressColor = (percentage: number) => {
  if (percentage > 90) return '#f56c6c'
  if (percentage > 70) return '#e6a23c'
  return '#67c23a'
}

const getAlertIcon = (level: string) => {
  switch (level) {
    case 'critical': return 'CircleClose'
    case 'error': return 'CircleClose'
    case 'warning': return 'Warning'
    case 'info': return 'InfoFilled'
    default: return 'InfoFilled'
  }
}

const getAlertLevelName = (level: string) => {
  switch (level) {
    case 'critical': return '严重'
    case 'error': return '错误'
    case 'warning': return '警告'
    case 'info': return '信息'
    default: return '未知'
  }
}

const getLogIcon = (level: string) => {
  switch (level) {
    case 'error': return 'CircleClose'
    case 'warning': return 'Warning'
    case 'info': return 'InfoFilled'
    case 'debug': return 'InfoFilled'
    default: return 'InfoFilled'
  }
}

const getLogLevelName = (level: string) => {
  switch (level) {
    case 'error': return '错误'
    case 'warning': return '警告'
    case 'info': return '信息'
    case 'debug': return '调试'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.monitoring {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.overview-section,
.alerts-section,
.logs-section,
.dashboards-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 24px;
}

.metric-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-title {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.metric-icon {
  font-size: 20px;
  color: #409EFF;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.metric-chart {
  margin-bottom: 8px;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-icon {
  font-size: 16px;
  color: #67C23A;
}

.trend-text {
  font-size: 12px;
  color: #67C23A;
  font-weight: 500;
}

.alerts-list,
.logs-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 0 24px 24px;
}

.alert-item,
.log-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  transition: all 0.3s ease;
}

.alert-item:hover,
.log-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alert-critical {
  border-left: 4px solid #f56c6c;
}

.alert-error {
  border-left: 4px solid #f56c6c;
}

.alert-warning {
  border-left: 4px solid #e6a23c;
}

.alert-info {
  border-left: 4px solid #409eff;
}

.log-error {
  border-left: 4px solid #f56c6c;
}

.log-warning {
  border-left: 4px solid #e6a23c;
}

.log-info {
  border-left: 4px solid #409eff;
}

.log-debug {
  border-left: 4px solid #909399;
}

.alert-header,
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.alert-level,
.log-level {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.alert-time,
.log-time {
  font-size: 12px;
  color: #909399;
}

.alert-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.alert-content p {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.4;
}

.alert-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-source {
  font-size: 12px;
  color: #909399;
}

.log-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-message {
  color: #303133;
  line-height: 1.4;
}

.log-source {
  font-size: 12px;
  color: #909399;
}

.dashboards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 24px;
}

.dashboard-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dashboard-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.dashboard-description {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.dashboard-stats {
  display: flex;
  gap: 16px;
}

.stat {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .dashboards-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
