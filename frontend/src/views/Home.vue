<template>
  <div class="home-page">
    <div class="hero-section">
      <h1>AI工作流编排平台</h1>
      <p>集成LangGraph、CrewAI、AutoGen的智能工作流设计和管理平台</p>

      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/workflow')">
          <el-icon><VideoPlay /></el-icon>
          开始设计工作流
        </el-button>
        <el-button size="large" @click="$router.push('/agents')">
          <el-icon><User /></el-icon>
          管理智能体
        </el-button>
      </div>
    </div>

    <div class="features-section">
      <div class="container">
        <h2>核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <h3>工作流设计</h3>
            <p>可视化设计AI工作流程，支持拖拽式节点编辑</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><User /></el-icon>
            </div>
            <h3>智能体管理</h3>
            <p>管理LangGraph、CrewAI、AutoGen智能体</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><Document /></el-icon>
            </div>
            <h3>RAG系统</h3>
            <p>知识库管理和文档检索增强生成</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <h3>实时监控</h3>
            <p>工作流执行状态监控和性能分析</p>
          </div>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">工作流</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">智能体</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">知识库</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">执行次数</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElButton, ElIcon } from 'element-plus'
import { VideoPlay, User, Connection, Document, Monitor } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero-section {
  text-align: center;
  padding: 80px 20px;
  color: white;
}

.hero-section h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-section p {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section {
  background: white;
  padding: 80px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.features-section h2 {
  text-align: center;
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 60px;
  color: #303133;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 40px;
}

.feature-card {
  text-align: center;
  padding: 40px 20px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

.stats-section {
  background: #f5f5f5;
  padding: 60px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 48px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 36px;
  }

  .hero-section p {
    font-size: 18px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
