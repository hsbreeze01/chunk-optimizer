# Chunk Optimizer 客户端 SDK 规格

## 概述

本文档详细描述 Chunk Optimizer 的客户端 SDK，包括 Python SDK 和 JavaScript/TypeScript SDK 的 API、使用方法和最佳实践。

---

## Python SDK

### 基本信息

**包名**: `chunk-optimizer-client`

**版本**: 0.1.0

**依赖**:
- Python >= 3.10
- pydantic >= 2.5.0
- httpx >= 0.25.2
- aiohttp >= 3.9.1

**安装**:
```bash
pip install chunk-optimizer-client
```

### 数据模型

#### Optimization（优化建议）

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Optimization(BaseModel):
    id: str = Field(..., description="优化建议唯一标识符")
    chunk_id: str = Field(..., description="Chunk ID")
    type: str = Field(..., description="优化类型")
    priority: str = Field(..., description="优先级: low|medium|high")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    suggested_action: str = Field(..., description="建议行动")
    related_chunks: List[str] = Field(default_factory=list, description="相关 Chunk ID 列表")
    created_at: datetime = Field(..., description="创建时间")
    status: str = Field(default="pending", description="状态: pending|applied|ignored")
```

#### Metrics（指标）

```python
class Metrics(BaseModel):
    chunk_id: str = Field(..., description="Chunk ID")
    quality_score: float = Field(..., ge=0, le=1, description="质量分数")
    redundancy_score: float = Field(..., ge=0, le=1, description="冗余分数")
    size_score: float = Field(..., ge=0, le=1, description="大小分数")
    similarity_score: float = Field(..., ge=0, le=1, description="相似度分数")
    overall_score: float = Field(..., ge=0, le=1, description="综合分数")
```

#### Chunk（Chunk 对象）

```python
class Chunk(BaseModel):
    chunk_id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk 内容")
    metadata: Optional[dict] = Field(default=None, description="元数据")
```

#### AnalysisOptions（分析选项）

```python
class AnalysisOptions(BaseModel):
    check_quality: bool = Field(default=True, description="是否检查质量")
    check_redundancy: bool = Field(default=True, description="是否检查冗余")
    check_size: bool = Field(default=True, description="是否检查大小")
    check_similarity: bool = Field(default=True, description="是否检查相似度")
    similarity_threshold: float = Field(default=0.85, ge=0, le=1, description="相似度阈值")
```

### 异步客户端

#### ChunkOptimizerClient

```python
from typing import List, Optional, Tuple
import httpx


class ChunkOptimizerClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        enable_cache: bool = True,
        cache_size: int = 1000,
        cache_ttl: int = 3600
    ):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥（Phase 2）
            timeout: 请求超时时间（秒）
            enable_cache: 是否启用缓存
            cache_size: 缓存大小
            cache_ttl: 缓存过期时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache = {} if enable_cache else None
        self.cache_ttl = cache_ttl
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers()
            )
    
    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "chunk-optimizer-client/0.1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None
    ) -> dict:
        await self._ensure_client()
        
        response = await self._client.request(
            method=method,
            path=path,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def _get_from_cache(self, key: str) -> Optional[Tuple[Optimization, Metrics]]:
        if not self.enable_cache or not self.cache:
            return None
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
            else:
                del self.cache[key]
        
        return None
    
    def _set_cache(self, key: str, value: Tuple[Optimization, Metrics]):
        if not self.enable_cache or not self.cache:
            return
        
        if len(self.cache) >= self.cache_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, time.time())
    
    async def analyze_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Tuple[Optimization, Metrics]:
        """
        分析单个 Chunk
        
        Args:
            chunk_id: Chunk ID
            content: Chunk 内容
            metadata: 可选的元数据
        
        Returns:
            (Optimization, Metrics)
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        cache_key = f"chunk:{chunk_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        data = {
            "chunk_id": chunk_id,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = await self._request("POST", "/api/v1/chunks/analyze", data)
        
        optimization = Optimization(**response["optimization"])
        metrics = Metrics(**response["metrics"])
        
        result = (optimization, metrics)
        self._set_cache(cache_key, result)
        
        return result
    
    async def analyze_document(
        self,
        document_id: str,
        chunks: List[Chunk],
        options: Optional[AnalysisOptions] = None
    ) -> List[Optimization]:
        """
        分析文档的所有 Chunk
        
        Args:
            document_id: 文档 ID
            chunks: Chunk 列表
            options: 分析选项
        
        Returns:
            优化建议列表
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        data = {
            "document_id": document_id,
            "chunks": [chunk.model_dump() for chunk in chunks],
            "options": options.model_dump() if options else {}
        }
        
        response = await self._request("POST", "/api/v1/documents/analyze", data)
        
        return [Optimization(**opt) for opt in response["optimizations"]]
    
    async def analyze_batch(
        self,
        items: List[Chunk],
        options: Optional[AnalysisOptions] = None
    ) -> dict:
        """
        批量分析 Chunks
        
        Args:
            items: Chunk 列表
            options: 分析选项
        
        Returns:
            批量分析结果
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        batch_id = str(uuid.uuid4())
        data = {
            "batch_id": batch_id,
            "items": [item.model_dump() for item in items],
            "options": options.model_dump() if options else {}
        }
        
        response = await self._request("POST", "/api/v1/batch/analyze", data)
        
        return response
    
    async def calculate_similarity(
        self,
        content1: str,
        content2: str
    ) -> float:
        """
        计算两个 Chunk 之间的相似度
        
        Args:
            content1: 第一个 Chunk 的内容
            content2: 第二个 Chunk 的内容
        
        Returns:
            相似度分数 (0-1)
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        data = {
            "content1": content1,
            "content2": content2
        }
        
        response = await self._request("POST", "/api/v1/similarity/calculate", data)
        
        return response["similarity_score"]
    
    async def health_check(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            服务是否健康
        """
        try:
            response = await self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception:
            return False
    
    def clear_cache(self) -> None:
        """
        清空缓存
        """
        if self.cache:
            self.cache.clear()
    
    async def close(self) -> None:
        """
        关闭客户端
        """
        if self._client:
            await self._client.aclose()
            self._client = None
```

### 同步客户端

#### SyncChunkOptimizerClient

```python
from typing import List, Optional, Tuple
import httpx


class SyncChunkOptimizerClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        enable_cache: bool = True,
        cache_size: int = 1000,
        cache_ttl: int = 3600
    ):
        """
        初始化同步客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥（Phase 2）
            timeout: 请求超时时间（秒）
            enable_cache: 是否启用缓存
            cache_size: 缓存大小
            cache_ttl: 缓存过期时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache = {} if enable_cache else None
        self.cache_ttl = cache_ttl
        
        self._client: Optional[httpx.Client] = None
    
    def __enter__(self):
        self._ensure_client()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _ensure_client(self):
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers()
            )
    
    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "chunk-optimizer-client/0.1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None
    ) -> dict:
        self._ensure_client()
        
        response = self._client.request(
            method=method,
            path=path,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def analyze_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Tuple[Optimization, Metrics]:
        """
        分析单个 Chunk（同步）
        
        Args:
            chunk_id: Chunk ID
            content: Chunk 内容
            metadata: 可选的元数据
        
        Returns:
            (Optimization, Metrics)
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        cache_key = f"chunk:{chunk_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        data = {
            "chunk_id": chunk_id,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = self._request("POST", "/api/v1/chunks/analyze", data)
        
        optimization = Optimization(**response["optimization"])
        metrics = Metrics(**response["metrics"])
        
        result = (optimization, metrics)
        self._set_cache(cache_key, result)
        
        return result
    
    def analyze_document(
        self,
        document_id: str,
        chunks: List[Chunk],
        options: Optional[AnalysisOptions] = None
    ) -> List[Optimization]:
        """
        分析文档的所有 Chunk（同步）
        
        Args:
            document_id: 文档 ID
            chunks: Chunk 列表
            options: 分析选项
        
        Returns:
            优化建议列表
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        data = {
            "document_id": document_id,
            "chunks": [chunk.model_dump() for chunk in chunks],
            "options": options.model_dump() if options else {}
        }
        
        response = self._request("POST", "/api/v1/documents/analyze", data)
        
        return [Optimization(**opt) for opt in response["optimizations"]]
    
    def analyze_batch(
        self,
        items: List[Chunk],
        options: Optional[AnalysisOptions] = None
    ) -> dict:
        """
        批量分析 Chunks（同步）
        
        Args:
            items: Chunk 列表
            options: 分析选项
        
        Returns:
            批量分析结果
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        batch_id = str(uuid.uuid4())
        data = {
            "batch_id": batch_id,
            "items": [item.model_dump() for item in items],
            "options": options.model_dump() if options else {}
        }
        
        response = self._request("POST", "/api/v1/batch/analyze", data)
        
        return response
    
    def calculate_similarity(
        self,
        content1: str,
        content2: str
    ) -> float:
        """
        计算两个 Chunk 之间的相似度（同步）
        
        Args:
            content1: 第一个 Chunk 的内容
            content2: 第二个 Chunk 的内容
        
        Returns:
            相似度分数 (0-1)
        
        Raises:
            ChunkOptimizerError: 请求失败
        """
        data = {
            "content1": content1,
            "content2": content2
        }
        
        response = self._request("POST", "/api/v1/similarity/calculate", data)
        
        return response["similarity_score"]
    
    def health_check(self) -> bool:
        """
        检查服务健康状态（同步）
        
        Returns:
            服务是否健康
        """
        try:
            response = self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception:
            return False
    
    def clear_cache(self) -> None:
        """
        清空缓存
        """
        if self.cache:
            self.cache.clear()
    
    def close(self) -> None:
        """
        关闭客户端
        """
        if self._client:
            self._client.close()
            self._client = None
```

### 异常处理

#### ChunkOptimizerError

```python
class ChunkOptimizerError(Exception):
    """基础异常类"""
    pass


class ConnectionError(ChunkOptimizerError):
    """连接错误"""
    pass


class TimeoutError(ChunkOptimizerError):
    """超时错误"""
    pass


class ValidationError(ChunkOptimizerError):
    """验证错误"""
    pass


class AuthenticationError(ChunkOptimizerError):
    """认证错误（Phase 2）"""
    pass


class RateLimitError(ChunkOptimizerError):
    """限流错误（Phase 2）"""
    pass
```

### 使用示例

#### 异步客户端

```python
import asyncio
from chunk_optimizer import ChunkOptimizerClient, Chunk


async def main():
    async with ChunkOptimizerClient(
        base_url="http://localhost:8000",
        enable_cache=True
    ) as client:
        # 分析单个 Chunk
        optimization, metrics = await client.analyze_chunk(
            chunk_id="chunk-001",
            content="This is a sample chunk content...",
            metadata={"source_file": "document.pdf", "page": 1}
        )
        
        print(f"Quality score: {metrics.quality_score}")
        print(f"Optimization: {optimization.title}")
        
        # 分析文档
        chunks = [
            Chunk(chunk_id="chunk-001", content="First chunk..."),
            Chunk(chunk_id="chunk-002", content="Second chunk...")
        ]
        optimizations = await client.analyze_document(
            document_id="doc-001",
            chunks=chunks
        )
        
        print(f"Total optimizations: {len(optimizations)}")
        
        # 批量分析
        results = await client.analyze_batch(chunks)
        print(f"Processed: {results['processed']}/{results['total']}")
        
        # 计算相似度
        similarity = await client.calculate_similarity(
            content1="First chunk...",
            content2="Second chunk..."
        )
        print(f"Similarity: {similarity}")


if __name__ == "__main__":
    asyncio.run(main())
```

#### 同步客户端

```python
from chunk_optimizer import SyncChunkOptimizerClient, Chunk


def main():
    with SyncChunkOptimizerClient(
        base_url="http://localhost:8000",
        enable_cache=True
    ) as client:
        # 分析单个 Chunk
        optimization, metrics = client.analyze_chunk(
            chunk_id="chunk-001",
            content="This is a sample chunk content...",
            metadata={"source_file": "document.pdf", "page": 1}
        )
        
        print(f"Quality score: {metrics.quality_score}")
        print(f"Optimization: {optimization.title}")
        
        # 分析文档
        chunks = [
            Chunk(chunk_id="chunk-001", content="First chunk..."),
            Chunk(chunk_id="chunk-002", content="Second chunk...")
        ]
        optimizations = client.analyze_document(
            document_id="doc-001",
            chunks=chunks
        )
        
        print(f"Total optimizations: {len(optimizations)}")


if __name__ == "__main__":
    main()
```

---

## JavaScript/TypeScript SDK

### 基本信息

**包名**: `chunk-optimizer-js-client`

**版本**: 0.1.0

**依赖**:
- TypeScript >= 5.0
- Node.js >= 18

**安装**:
```bash
npm install chunk-optimizer-js-client
```

### 数据模型

```typescript
export interface Optimization {
  id: string;
  chunk_id: string;
  type: 'quality' | 'redundancy' | 'size' | 'similarity' | 'info';
  priority: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  suggested_action: string;
  related_chunks: string[];
  created_at: string;
  status: 'pending' | 'applied' | 'ignored';
}

export interface Metrics {
  chunk_id: string;
  quality_score: number;
  redundancy_score: number;
  size_score: number;
  similarity_score: number;
  overall_score: number;
}

export interface Chunk {
  chunk_id: string;
  content: string;
  metadata?: Record<string, any>;
}

export interface OptimizationOptions {
  check_quality?: boolean;
  check_redundancy?: boolean;
  check_size?: boolean;
  check_similarity?: boolean;
  similarity_threshold?: number;
}

export interface ChunkOptimizerConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  enableCache?: boolean;
  cacheSize?: number;
  cacheTTL?: number;
}

export interface BatchResult {
  batch_id: string;
  results: Array<{
    item_id: string;
    optimization: Optimization;
    metrics: Metrics;
  }>;
  processed: number;
  total: number;
  failed: number;
}
```

### 客户端实现

```typescript
export class ChunkOptimizerClient {
  private config: Required<ChunkOptimizerConfig>;
  private cache: Map<string, { value: any; timestamp: number }> = new Map();

  constructor(config: ChunkOptimizerConfig = {}) {
    this.config = {
      baseUrl: config.baseUrl || 'http://localhost:8000',
      apiKey: config.apiKey || '',
      timeout: config.timeout || 30000,
      enableCache: config.enableCache !== false,
      cacheSize: config.cacheSize || 1000,
      cacheTTL: config.cacheTTL || 3600,
    };
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'chunk-optimizer-js-client/0.1.0',
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    return headers;
  }

  private async request<T>(
    method: string,
    path: string,
    data?: any
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const options: RequestInit = {
      method,
      headers: this.getHeaders(),
      signal: AbortSignal.timeout(this.config.timeout),
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      throw new ChunkOptimizerError(
        `Request failed: ${response.status} ${response.statusText}`
      );
    }

    return response.json();
  }

  private getFromCache(key: string): any {
    if (!this.config.enableCache) {
      return null;
    }

    const cached = this.cache.get(key);
    if (cached) {
      const now = Math.floor(Date.now() / 1000);
      if (now - cached.timestamp < this.config.cacheTTL) {
        return cached.value;
      } else {
        this.cache.delete(key);
      }
    }

    return null;
  }

  private setCache(key: string, value: any): void {
    if (!this.config.enableCache) {
      return;
    }

    if (this.cache.size >= this.config.cacheSize) {
      const oldestKey = Array.from(this.cache.keys())[0];
      this.cache.delete(oldestKey);
    }

    const timestamp = Math.floor(Date.now() / 1000);
    this.cache.set(key, { value, timestamp });
  }

  async analyzeChunk(
    chunkId: string,
    content: string,
    metadata?: Record<string, any>
  ): Promise<{ optimization: Optimization; metrics: Metrics }> {
    const cacheKey = `chunk:${chunkId}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

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
    const result = await this.request<BatchResult>('/api/v1/batch/analyze', 'POST', {
      batch_id: batchId,
      items,
      options: options || {},
    });

    return result;
  }

  async calculateSimilarity(
    content1: string,
    content2: string
  ): Promise<number> {
    const result = await this.request<{
      similarity_score: number;
    }>('/api/v1/similarity/calculate', 'POST', {
      content1,
      content2,
    });

    return result.similarity_score;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const result = await this.request<{
        status: string;
      }>('/health', 'GET');

      return result.status === 'healthy';
    } catch (error) {
      return false;
    }
  }

  clearCache(): void {
    this.cache.clear();
  }
}

export class ChunkOptimizerError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ChunkOptimizerError';
  }
}

export class ConnectionError extends ChunkOptimizerError {
  constructor(message: string) {
    super(message);
    this.name = 'ConnectionError';
  }
}

export class TimeoutError extends ChunkOptimizerError {
  constructor(message: string) {
    super(message);
    this.name = 'TimeoutError';
  }
}

export class ValidationError extends ChunkOptimizerError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends ChunkOptimizerError {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends ChunkOptimizerError {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}
```

### 使用示例

```typescript
import { ChunkOptimizerClient, Chunk } from 'chunk-optimizer-js-client';

async function main() {
  const client = new ChunkOptimizerClient({
    baseUrl: 'http://localhost:8000',
    enableCache: true,
  });

  try {
    // 分析单个 Chunk
    const { optimization, metrics } = await client.analyzeChunk(
      'chunk-001',
      'This is a sample chunk content...',
      { source_file: 'document.pdf', page: 1 }
    );

    console.log(`Quality score: ${metrics.quality_score}`);
    console.log(`Optimization: ${optimization.title}`);

    // 分析文档
    const chunks: Chunk[] = [
      { chunk_id: 'chunk-001', content: 'First chunk...' },
      { chunk_id: 'chunk-002', content: 'Second chunk...' },
    ];

    const result = await client.analyzeDocument('doc-001', chunks);
    console.log(`Total optimizations: ${result.total}`);

    // 批量分析
    const batchResult = await client.analyzeBatch(chunks);
    console.log(`Processed: ${batchResult.processed}/${batchResult.total}`);

    // 计算相似度
    const similarity = await client.calculateSimilarity(
      'First chunk...',
      'Second chunk...'
    );
    console.log(`Similarity: ${similarity}`);

    // 健康检查
    const healthy = await client.healthCheck();
    console.log(`Service healthy: ${healthy}`);

  } catch (error) {
    if (error instanceof ChunkOptimizerError) {
      console.error(`Chunk Optimizer Error: ${error.message}`);
    } else {
      console.error(`Unexpected error: ${error}`);
    }
  }
}

main();
```

---

## 最佳实践

### Python SDK

1. **使用上下文管理器**:
   ```python
   async with ChunkOptimizerClient() as client:
       # 使用客户端
       pass
   ```

2. **启用缓存**:
   ```python
   client = ChunkOptimizerClient(enable_cache=True)
   ```

3. **批量处理**:
   ```python
   # 使用批量分析代替单个分析
   results = await client.analyze_batch(chunks)
   ```

4. **错误处理**:
   ```python
   try:
       optimization, metrics = await client.analyze_chunk(...)
   except ChunkOptimizerError as e:
       print(f"Error: {e}")
   ```

5. **资源清理**:
   ```python
   await client.close()
   ```

### JavaScript/TypeScript SDK

1. **启用缓存**:
   ```typescript
   const client = new ChunkOptimizerClient({
     enableCache: true,
   });
   ```

2. **批量处理**:
   ```typescript
   const result = await client.analyzeBatch(chunks);
   ```

3. **错误处理**:
   ```typescript
   try {
     const result = await client.analyzeChunk(...);
   } catch (error) {
     if (error instanceof ChunkOptimizerError) {
       console.error(`Error: ${error.message}`);
     }
   }
   ```

4. **清空缓存**:
   ```typescript
   client.clearCache();
   ```

---

## 性能优化

### Python SDK

1. **使用异步客户端**: 提高并发性能
2. **启用缓存**: 减少重复请求
3. **批量处理**: 减少网络开销
4. **连接池**: 复用 HTTP 连接

### JavaScript/TypeScript SDK

1. **启用缓存**: 减少重复请求
2. **批量处理**: 减少网络开销
3. **使用 fetch API**: 利用浏览器缓存
4. **使用 Web Workers**: 避免阻塞 UI 线程

---

## 测试

### Python SDK

```python
import pytest
from chunk_optimizer import ChunkOptimizerClient, ChunkOptimizerError


@pytest.mark.asyncio
async def test_analyze_chunk():
    async with ChunkOptimizerClient() as client:
        optimization, metrics = await client.analyze_chunk(
            chunk_id="test-001",
            content="Test content"
        )
        
        assert optimization.chunk_id == "test-001"
        assert 0 <= metrics.quality_score <= 1


@pytest.mark.asyncio
async def test_error_handling():
    async with ChunkOptimizerClient(base_url="http://invalid") as client:
        with pytest.raises(ChunkOptimizerError):
            await client.analyze_chunk(
                chunk_id="test-001",
                content="Test content"
            )
```

### JavaScript/TypeScript SDK

```typescript
import { describe, it, expect } from 'vitest';
import { ChunkOptimizerClient, ChunkOptimizerError } from 'chunk-optimizer-js-client';

describe('ChunkOptimizerClient', () => {
  it('should analyze a chunk', async () => {
    const client = new ChunkOptimizerClient();
    const { optimization, metrics } = await client.analyzeChunk(
      'test-001',
      'Test content'
    );

    expect(optimization.chunk_id).toBe('test-001');
    expect(metrics.quality_score).toBeGreaterThanOrEqual(0);
    expect(metrics.quality_score).toBeLessThanOrEqual(1);
  });

  it('should handle errors', async () => {
    const client = new ChunkOptimizerClient({
      baseUrl: 'http://invalid',
    });

    await expect(
      client.analyzeChunk('test-001', 'Test content')
    ).rejects.toThrow(ChunkOptimizerError);
  });
});
```

---

## 未来扩展

### Phase 2

- WebSocket 支持
- 流式响应
- 自定义分析选项
- 高级过滤和搜索

### Phase 3

- 离线模式
- 本地缓存持久化
- 请求重试策略
- 请求拦截器
