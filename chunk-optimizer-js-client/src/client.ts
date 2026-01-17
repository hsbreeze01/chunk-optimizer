interface ChunkOptimizerConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  enableCache?: boolean;
  cacheTTL?: number;
}

import type {
  Optimization,
  Metrics,
  OptimizationOptions,
  BatchResult,
  Chunk,
} from './models';
import {
  ChunkOptimizerError,
  AuthenticationError,
  RateLimitError,
  NetworkError,
} from './exceptions';

class ChunkOptimizerClient {
  private config: Required<ChunkOptimizerConfig>;
  private cache: Map<string, { data: any; expiry: number }>;

  constructor(config: ChunkOptimizerConfig) {
    this.config = {
      apiKey: config.apiKey,
      baseUrl: config.baseUrl || 'http://localhost:8000',
      timeout: config.timeout || 30000,
      enableCache: config.enableCache ?? true,
      cacheTTL: config.cacheTTL || 3600000,
    };
    this.cache = new Map();
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 401) {
        throw new AuthenticationError('Invalid API key');
      }

      if (response.status === 429) {
        throw new RateLimitError('Rate limit exceeded');
      }

      if (!response.ok) {
        const error = await response.text();
        throw new ChunkOptimizerError(`API error: ${error}`);
      }

      return await response.json();
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new NetworkError('Request timeout');
      }
      if (error instanceof ChunkOptimizerError) {
        throw error;
      }
      throw new NetworkError(`Network error: ${error.message}`);
    }
  }

  private getFromCache(key: string): any | null {
    if (!this.config.enableCache) return null;

    const cached = this.cache.get(key);
    if (!cached) return null;

    if (Date.now() > cached.expiry) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  private setCache(key: string, data: any): void {
    if (!this.config.enableCache) return;

    this.cache.set(key, {
      data,
      expiry: Date.now() + this.config.cacheTTL,
    });
  }

  async analyzeChunk(
    chunkId: string,
    content: string,
    metadata?: Record<string, any>
  ): Promise<{ optimization: Optimization; metrics: Metrics }> {
    const cacheKey = `chunk:${chunkId}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) return cached;

    const result = await this.request<{
      optimization: Optimization;
      metrics: Metrics;
    }>('/api/v1/chunks/analyze', 'POST', {
      chunk_id: chunkId,
      content,
      metadata: metadata || {},
    });

    this.setCache(cacheKey, result);
    return result;
  }

  async analyzeDocument(
    documentId: string,
    chunks: Chunk[],
    options?: OptimizationOptions
  ): Promise<{ optimizations: Optimization[]; total: number; high_priority: number }> {
    const result = await this.request<{
      optimizations: Optimization[];
      total: number;
      high_priority: number;
    }>('/api/v1/documents/analyze', 'POST', {
      document_id: documentId,
      chunks,
      options: options || {},
    });

    return result;
  }

  async analyzeBatch(
    items: Chunk[],
    options?: OptimizationOptions
  ): Promise<BatchResult> {
    const batchId = crypto.randomUUID();
    const result = await this.request<{
      batch_id: string;
      item_id: string;
      optimization: Optimization | null;
      processed: number;
      total: number;
    }>('/api/v1/batch/analyze', 'POST', {
      batch_id: batchId,
      items,
      options: options || {},
    });

    return {
      batch_id: result.batch_id,
      total: items.length,
      processed: result.processed,
      optimizations: result.optimization ? [result.optimization] : [],
    };
  }

  clearCache(): void {
    this.cache.clear();
  }
}

export { ChunkOptimizerClient };
