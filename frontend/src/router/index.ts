import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/workflow',
    name: 'WorkflowDesigner',
    component: () => import('@/views/WorkflowDesigner.vue')
  },
  {
    path: '/agents',
    name: 'AgentManagement',
    component: () => import('@/views/AgentManagement.vue')
  },
  {
    path: '/rag',
    name: 'RAGManagement',
    component: () => import('@/views/RAGManagement.vue')
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('@/views/Monitoring.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
