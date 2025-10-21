<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <h2>AI工作流平台</h2>
        </div>

        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <el-menu-item index="/workflow">
            <el-icon><Connection /></el-icon>
            <span>工作流设计</span>
          </el-menu-item>

          <el-menu-item index="/agents">
            <el-icon><User /></el-icon>
            <span>智能体管理</span>
          </el-menu-item>

          <el-menu-item index="/rag">
            <el-icon><Document /></el-icon>
            <span>RAG系统</span>
          </el-menu-item>

          <el-menu-item index="/monitoring">
            <el-icon><Monitor /></el-icon>
            <span>监控中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ElContainer, ElAside, ElMain, ElMenu, ElMenuItem, ElIcon } from 'element-plus'
import { House, Connection, User, Document, Monitor } from '@element-plus/icons-vue'
</script>

<style>
#app {
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
}

.sidebar {
  background: #304156;
  color: white;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #434a50;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
  background: #304156;
}

.sidebar-menu .el-menu-item:hover {
  background: #263445;
  color: white;
}

.sidebar-menu .el-menu-item.is-active {
  background: #409EFF;
  color: white;
}

.main-content {
  padding: 0;
  background: #f5f5f5;
  overflow: auto;
}

/* 全局样式重置 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Vue Flow 样式 */
.vue-flow {
  background: #fafafa;
}

.vue-flow__node {
  cursor: pointer;
}

.vue-flow__edge {
  cursor: pointer;
}

.vue-flow__edge-path {
  stroke: #b1b1b7;
  stroke-width: 2;
}

.vue-flow__edge.selected .vue-flow__edge-path {
  stroke: #409EFF;
  stroke-width: 3;
}

.vue-flow__edge-text {
  font-size: 12px;
  fill: #606266;
}

.vue-flow__controls {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.vue-flow__minimap {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
