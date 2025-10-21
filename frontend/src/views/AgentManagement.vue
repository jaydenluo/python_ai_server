<template>
  <div class="agent-management">
    <div class="page-header">
      <h1>智能体管理</h1>
      <p>管理LangGraph、CrewAI、AutoGen智能体</p>

      <div class="header-actions">
        <el-button type="primary" @click="showCreateAgentDialog = true">
          <el-icon><Plus /></el-icon>
          创建智能体
        </el-button>
        <el-button @click="showCreateTeamDialog = true">
          <el-icon><UserFilled /></el-icon>
          创建团队
        </el-button>
      </div>
    </div>

    <div class="content">
      <!-- 智能体列表 -->
      <div class="agents-section">
        <div class="section-header">
          <h2>智能体列表</h2>
          <el-space>
            <el-select v-model="selectedType" placeholder="筛选类型" @change="filterAgents">
              <el-option label="全部" value="" />
              <el-option label="LangGraph" value="langgraph" />
              <el-option label="CrewAI" value="crewai" />
              <el-option label="AutoGen" value="autogen" />
            </el-select>
            <el-button @click="refreshAgents">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
        </div>

        <div class="agents-grid">
          <div
            v-for="agent in filteredAgents"
            :key="agent.id"
            class="agent-card"
            @click="selectAgent(agent)"
          >
            <div class="agent-header">
              <div class="agent-type">
                <el-icon>
                  <component :is="getAgentIcon(agent.type)" />
                </el-icon>
                {{ getAgentTypeName(agent.type) }}
              </div>
              <el-tag :type="getStatusType(agent.status)" size="small">
                {{ getStatusText(agent.status) }}
              </el-tag>
            </div>

            <div class="agent-info">
              <h3>{{ agent.name }}</h3>
              <p>{{ agent.role }}</p>
              <p class="agent-goal">{{ agent.goal }}</p>
            </div>

            <div class="agent-stats">
              <div class="stat">
                <span class="stat-label">成功率</span>
                <span class="stat-value">{{ agent.performance.success_rate }}%</span>
              </div>
              <div class="stat">
                <span class="stat-label">任务数</span>
                <span class="stat-value">{{ agent.performance.total_tasks }}</span>
              </div>
            </div>

            <div class="agent-actions">
              <el-button size="small" @click.stop="editAgent(agent)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="primary" @click.stop="executeAgent(agent)">
                <el-icon><VideoPlay /></el-icon>
                执行
              </el-button>
              <el-button size="small" type="danger" @click.stop="deleteAgent(agent)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 团队列表 -->
      <div class="teams-section">
        <div class="section-header">
          <h2>团队列表</h2>
          <el-button @click="refreshTeams">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div class="teams-grid">
          <div
            v-for="team in teams"
            :key="team.id"
            class="team-card"
            @click="selectTeam(team)"
          >
            <div class="team-header">
              <h3>{{ team.name }}</h3>
              <el-tag :type="team.status === 'active' ? 'success' : 'info'">
                {{ team.status === 'active' ? '活跃' : '非活跃' }}
              </el-tag>
            </div>

            <p class="team-description">{{ team.description }}</p>

            <div class="team-agents">
              <span class="agents-count">{{ team.agents.length }} 个智能体</span>
            </div>

            <div class="team-actions">
              <el-button size="small" @click.stop="editTeam(team)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="primary" @click.stop="executeTeam(team)">
                <el-icon><VideoPlay /></el-icon>
                执行
              </el-button>
              <el-button size="small" type="danger" @click.stop="deleteTeam(team)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建智能体对话框 -->
    <el-dialog
      v-model="showCreateAgentDialog"
      title="创建智能体"
      width="600px"
    >
      <AgentForm
        :agent="newAgent"
        @submit="createAgent"
        @cancel="showCreateAgentDialog = false"
      />
    </el-dialog>

    <!-- 创建团队对话框 -->
    <el-dialog
      v-model="showCreateTeamDialog"
      title="创建团队"
      width="600px"
    >
      <TeamForm
        :team="newTeam"
        :agents="agents"
        @submit="createTeam"
        @cancel="showCreateTeamDialog = false"
      />
    </el-dialog>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行智能体"
      width="500px"
    >
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="任务类型">
          <el-input v-model="executeForm.taskType" />
        </el-form-item>
        <el-form-item label="输入数据">
          <el-input
            v-model="executeForm.inputData"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的输入数据"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showExecuteDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute">确认执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElButton, ElIcon, ElSpace, ElSelect, ElOption, ElTag, ElDialog, ElForm, ElFormItem, ElInput, ElMessage } from 'element-plus'
import { Plus, UserFilled, Refresh, Edit, VideoPlay, Delete, Connection, User, ChatDotRound } from '@element-plus/icons-vue'
import { useAgentStore } from '@/stores/agent'
import type { Agent, AgentTeam } from '@/types/agent'
import AgentForm from '@/components/AgentManagement/AgentForm.vue'
import TeamForm from '@/components/AgentManagement/TeamForm.vue'

const agentStore = useAgentStore()

// 状态
const selectedType = ref('')
const showCreateAgentDialog = ref(false)
const showCreateTeamDialog = ref(false)
const showExecuteDialog = ref(false)
const selectedAgent = ref<Agent | null>(null)
const newAgent = ref<Partial<Agent>>({})
const newTeam = ref<Partial<AgentTeam>>({})
const executeForm = ref({
  taskType: '',
  inputData: '{}'
})

// 计算属性
const agents = computed(() => agentStore.agents)
const teams = computed(() => agentStore.teams)
const loading = computed(() => agentStore.loading)

const filteredAgents = computed(() => {
  if (!selectedType.value) return agents.value
  return agents.value.filter(agent => agent.type === selectedType.value)
})

// 生命周期
onMounted(() => {
  loadData()
})

// 数据加载
const loadData = async () => {
  try {
    await Promise.all([
      agentStore.listAgents(),
      agentStore.listTeams()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const refreshAgents = () => {
  agentStore.listAgents()
}

const refreshTeams = () => {
  agentStore.listTeams()
}

// 智能体操作
const selectAgent = (agent: Agent) => {
  selectedAgent.value = agent
}

const editAgent = (agent: Agent) => {
  // 实现编辑逻辑
  console.log('编辑智能体:', agent)
}

const deleteAgent = async (agent: Agent) => {
  try {
    await agentStore.deleteAgent(agent.id)
    ElMessage.success('智能体删除成功')
  } catch (error) {
    ElMessage.error('删除智能体失败')
  }
}

const executeAgent = (agent: Agent) => {
  selectedAgent.value = agent
  showExecuteDialog.value = true
}

const createAgent = async (agentData: Partial<Agent>) => {
  try {
    await agentStore.createAgent(agentData)
    showCreateAgentDialog.value = false
    newAgent.value = {}
    ElMessage.success('智能体创建成功')
  } catch (error) {
    ElMessage.error('创建智能体失败')
  }
}

// 团队操作
const selectTeam = (team: AgentTeam) => {
  console.log('选择团队:', team)
}

const editTeam = (team: AgentTeam) => {
  // 实现编辑逻辑
  console.log('编辑团队:', team)
}

const deleteTeam = async (team: AgentTeam) => {
  try {
    await agentStore.deleteTeam(team.id)
    ElMessage.success('团队删除成功')
  } catch (error) {
    ElMessage.error('删除团队失败')
  }
}

const executeTeam = (team: AgentTeam) => {
  // 实现团队执行逻辑
  console.log('执行团队:', team)
}

const createTeam = async (teamData: Partial<AgentTeam>) => {
  try {
    await agentStore.createTeam(teamData)
    showCreateTeamDialog.value = false
    newTeam.value = {}
    ElMessage.success('团队创建成功')
  } catch (error) {
    ElMessage.error('创建团队失败')
  }
}

// 执行确认
const confirmExecute = async () => {
  if (!selectedAgent.value) return

  try {
    const inputData = JSON.parse(executeForm.value.inputData)
    await agentStore.executeTask(selectedAgent.value.id, {
      type: executeForm.value.taskType,
      input: inputData
    })
    showExecuteDialog.value = false
    ElMessage.success('任务执行已开始')
  } catch (error) {
    ElMessage.error('执行任务失败')
  }
}

// 工具方法
const getAgentIcon = (type: string) => {
  switch (type) {
    case 'langgraph': return 'Connection'
    case 'crewai': return 'User'
    case 'autogen': return 'ChatDotRound'
    default: return 'User'
  }
}

const getAgentTypeName = (type: string) => {
  switch (type) {
    case 'langgraph': return 'LangGraph'
    case 'crewai': return 'CrewAI'
    case 'autogen': return 'AutoGen'
    default: return '未知'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'idle': return 'success'
    case 'running': return 'warning'
    case 'busy': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'idle': return '空闲'
    case 'running': return '运行中'
    case 'busy': return '忙碌'
    case 'error': return '错误'
    case 'offline': return '离线'
    default: return '未知'
  }
}

const filterAgents = () => {
  // 筛选逻辑已在计算属性中处理
}
</script>

<style scoped>
.agent-management {
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

.agents-section,
.teams-section {
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

.agents-grid,
.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 24px;
}

.agent-card,
.team-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.agent-card:hover,
.team-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.agent-type {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.agent-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.agent-info p {
  margin: 0 0 4px 0;
  color: #606266;
  font-size: 14px;
}

.agent-goal {
  color: #909399 !important;
  font-size: 12px !important;
  line-height: 1.4;
}

.agent-stats {
  display: flex;
  gap: 16px;
  margin: 16px 0;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.agent-actions,
.team-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.team-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.team-description {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.team-agents {
  margin-bottom: 16px;
}

.agents-count {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .agents-grid,
  .teams-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
