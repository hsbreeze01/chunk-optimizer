export interface Chunk {
  chunk_id: string;
  content: string;
  metadata?: Record<string, any>;
}

export interface Optimization {
  id: string;
  chunk_id: string;
  type: string;
  priority: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  suggested_action: string;
  related_chunks?: string[];
  created_at: Date;
  status: string;
}

export interface Metrics {
  chunk_id: string;
  quality_score: number;
  redundancy_score: number;
  size_score: number;
  similarity_score: number;
  overall_score: number;
}

export interface OptimizationOptions {
  check_quality?: boolean;
  check_redundancy?: boolean;
  check_size?: boolean;
  check_similarity?: boolean;
  similarity_threshold?: number;
}

export interface BatchResult {
  batch_id: string;
  total: number;
  processed: number;
  optimizations: Optimization[];
  failed?: string[];
}
