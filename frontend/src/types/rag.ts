/**
 * RAG系统相关类型定义
 */

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  vector_store_type: VectorStoreType
  embedding_model: EmbeddingModelType
  settings: KnowledgeBaseSettings
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
  document_count: number
  vector_count: number
  last_indexed?: string
}

export type VectorStoreType = 'pinecone' | 'weaviate' | 'qdrant' | 'chroma' | 'faiss'

export type EmbeddingModelType = 'openai' | 'huggingface' | 'local'

export interface KnowledgeBaseSettings {
  chunk_size: number
  chunk_overlap: number
  similarity_threshold: number
  max_results: number
}

export interface Document {
  id: string
  content: string
  metadata: DocumentMetadata
  chunks: DocumentChunk[]
  created_at: string
  updated_at: string
}

export interface DocumentMetadata {
  title?: string
  author?: string
  source?: string
  tags?: string[]
  language?: string
  [key: string]: any
}

export interface DocumentChunk {
  id: string
  content: string
  metadata: Record<string, any>
  embedding?: number[]
  created_at: string
}

export interface SearchResult {
  id: string
  content: string
  metadata: Record<string, any>
  score: number
  source: string
}

export interface RAGQuery {
  query: string
  knowledge_base_id: string
  top_k: number
  filters?: Record<string, any>
  similarity_threshold?: number
}

export interface RAGResponse {
  results: SearchResult[]
  query: string
  knowledge_base_id: string
  execution_time: number
  total_results: number
}
