/**
 * RAG系统状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KnowledgeBase, Document, RAGQuery, RAGResponse } from '@/types/rag'
import { ragAPI } from '@/services/api'

export const useRAGStore = defineStore('rag', () => {
  // 状态
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const documents = ref<Document[]>([])
  const searchResults = ref<RAGResponse[]>([])
  const currentKnowledgeBase = ref<KnowledgeBase | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeKnowledgeBases = computed(() =>
    knowledgeBases.value.filter(kb => kb.status === 'active')
  )

  const totalDocuments = computed(() =>
    knowledgeBases.value.reduce((sum, kb) => sum + kb.document_count, 0)
  )

  const totalVectors = computed(() =>
    knowledgeBases.value.reduce((sum, kb) => sum + kb.vector_count, 0)
  )

  // 知识库管理
  const createKnowledgeBase = async (kbConfig: Partial<KnowledgeBase>) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.createKnowledgeBase(kbConfig)
      const newKB = response.data

      knowledgeBases.value.push(newKB)
      return newKB
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建知识库失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getKnowledgeBase = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.getKnowledgeBase(id)
      currentKnowledgeBase.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取知识库失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateKnowledgeBase = async (id: string, updates: Partial<KnowledgeBase>) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.updateKnowledgeBase(id, updates)
      const updatedKB = response.data

      const index = knowledgeBases.value.findIndex(kb => kb.id === id)
      if (index !== -1) {
        knowledgeBases.value[index] = updatedKB
      }

      if (currentKnowledgeBase.value?.id === id) {
        currentKnowledgeBase.value = updatedKB
      }

      return updatedKB
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新知识库失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteKnowledgeBase = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      await ragAPI.deleteKnowledgeBase(id)

      knowledgeBases.value = knowledgeBases.value.filter(kb => kb.id !== id)

      if (currentKnowledgeBase.value?.id === id) {
        currentKnowledgeBase.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除知识库失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const listKnowledgeBases = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.listKnowledgeBases()
      knowledgeBases.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取知识库列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 文档管理
  const uploadDocuments = async (kbId: string, documents: Document[]) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.uploadDocuments(kbId, documents)
      const uploadedDocs = response.data

      documents.value.push(...uploadedDocs)
      return uploadedDocs
    } catch (err) {
      error.value = err instanceof Error ? err.message : '上传文档失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDocuments = async (kbId: string, documentIds: string[]) => {
    try {
      loading.value = true
      error.value = null

      await ragAPI.deleteDocuments(kbId, documentIds)

      documents.value = documents.value.filter(doc => !documentIds.includes(doc.id))
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除文档失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getDocuments = async (kbId: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.getDocuments(kbId)
      documents.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取文档列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 搜索功能
  const searchDocuments = async (query: RAGQuery) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.searchDocuments(query)
      const searchResult = response.data

      searchResults.value.push(searchResult)
      return searchResult
    } catch (err) {
      error.value = err instanceof Error ? err.message : '搜索文档失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearSearchResults = () => {
    searchResults.value = []
  }

  // 统计信息
  const getKnowledgeBaseStats = async (id: string) => {
    try {
      loading.value = true
      error.value = null

      const response = await ragAPI.getKnowledgeBaseStats(id)
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取统计信息失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 工具方法
  const clearError = () => {
    error.value = null
  }

  const resetCurrentKnowledgeBase = () => {
    currentKnowledgeBase.value = null
  }

  return {
    // 状态
    knowledgeBases,
    documents,
    searchResults,
    currentKnowledgeBase,
    loading,
    error,

    // 计算属性
    activeKnowledgeBases,
    totalDocuments,
    totalVectors,

    // 知识库管理
    createKnowledgeBase,
    getKnowledgeBase,
    updateKnowledgeBase,
    deleteKnowledgeBase,
    listKnowledgeBases,

    // 文档管理
    uploadDocuments,
    deleteDocuments,
    getDocuments,

    // 搜索功能
    searchDocuments,
    clearSearchResults,

    // 统计信息
    getKnowledgeBaseStats,

    // 工具方法
    clearError,
    resetCurrentKnowledgeBase
  }
})
