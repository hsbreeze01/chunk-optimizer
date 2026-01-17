# Client SDK Layer Specification

## Responsibility

* 提供客户端 SDK
* 封装 HTTP 请求
* 提供类型安全的 API
* 支持异步和同步调用

## Scope

### Python Client SDK

`chunk-optimizer-client/src/chunk_optimizer/`

### JavaScript/TypeScript Client SDK

`chunk-optimizer-js-client/src/`

## Allowed Files

### Python Client SDK

* `client.py` - 异步客户端
* `sync_client.py` - 同步客户端
* `models.py` - 数据模型
* `exceptions.py` - 异常定义

### JavaScript/TypeScript Client SDK

* `client.ts` - 客户端实现
* `models.ts` - 数据模型
* `exceptions.ts` - 异常定义

## Dependencies

### Python Client SDK

* `httpx` - HTTP 客户端
* `pydantic` - 数据验证

### JavaScript/TypeScript Client SDK

* `fetch` - HTTP 客户端（浏览器原生）
* TypeScript 类型系统

## Forbidden

* 包含业务规则（业务规则在 service 层）
* 直接访问数据库
* 直接调用第三方 API（除了 API 服务）

## Implementation Requirements

### Python Client SDK

#### ChunkOptimizerClient (Async)

* **Methods**:
  * `__init__(base_url: str, api_key: str, timeout: float, enable_cache: bool, cache_size: int, cache_ttl: int)`
  * `async analyze_chunk(chunk_id: str, content: str, metadata: dict) -> Tuple[Optimization, Metrics]`
  * `async analyze_document(document_id: str, chunks: List[Chunk], options: AnalysisOptions) -> List[Optimization]`
  * `async analyze_batch(items: List[Chunk], options: AnalysisOptions) -> dict`
  * `async calculate_similarity(content1: str, content2: str) -> float`
  * `async health_check() -> bool`
  * `clear_cache() -> None`
  * `async close() -> None`

#### SyncChunkOptimizerClient

* **Methods**:
  * `__init__(base_url: str, api_key: str, timeout: float, enable_cache: bool, cache_size: int, cache_ttl: int)`
  * `analyze_chunk(chunk_id: str, content: str, metadata: dict) -> Tuple[Optimization, Metrics]`
  * `analyze_document(document_id: str, chunks: List[Chunk], options: AnalysisOptions) -> List[Optimization]`
  * `analyze_batch(items: List[Chunk], options: AnalysisOptions) -> dict`
  * `calculate_similarity(content1: str, content2: str) -> float`
  * `health_check() -> bool`
  * `clear_cache() -> None`
  * `close() -> None`

#### Caching

* 实现 LRU 缓存
* 支持缓存大小配置
* 支持缓存 TTL 配置
* 缓存键格式: `chunk:{chunk_id}`

#### Context Manager

* 异步客户端支持 `async with`
* 同步客户端支持 `with`

### JavaScript/TypeScript Client SDK

#### ChunkOptimizerClient

* **Methods**:
  * `constructor(config: ChunkOptimizerConfig)`
  * `analyzeChunk(chunkId: string, content: string, metadata?: Record<string, any>) -> Promise<{ optimization: Optimization; metrics: Metrics }>`
  * `analyzeDocument(documentId: string, chunks: Chunk[], options?: OptimizationOptions) -> Promise<{ optimizations: Optimization[]; total: number; high_priority: number }>`
  * `analyzeBatch(items: Chunk[], options?: OptimizationOptions) -> Promise<BatchResult>`
  * `calculateSimilarity(content1: string, content2: string) -> Promise<number>`
  * `healthCheck() -> Promise<boolean>`
  * `clearCache() -> void`

#### Caching

* 实现 Map 缓存
* 支持缓存大小配置
* 支持缓存 TTL 配置
* 缓存键格式: `chunk:{chunkId}`

### Data Models

所有数据模型必须参考 `spec/004-client-sdks.md`：

* `Optimization` - 优化建议
* `Metrics` - 指标
* `Chunk` - Chunk 对象
* `AnalysisOptions` / `OptimizationOptions` - 分析选项
* `ChunkOptimizerConfig` - 客户端配置

### Error Handling

所有异常必须继承自基类：

#### Python Client SDK

* `ChunkOptimizerError` - 基础异常类
* `ConnectionError` - 连接错误
* `TimeoutError` - 超时错误
* `ValidationError` - 验证错误
* `AuthenticationError` - 认证错误（Phase 2）
* `RateLimitError` - 限流错误（Phase 2）

#### JavaScript/TypeScript Client SDK

* `ChunkOptimizerError` - 基础异常类
* `ConnectionError` - 连接错误
* `TimeoutError` - 超时错误
* `ValidationError` - 验证错误
* `AuthenticationError` - 认证错误（Phase 2）
* `RateLimitError` - 限流错误（Phase 2）

## Testing Requirements

* 所有方法必须有单元测试
* 测试覆盖率 >= 80%
* 必须测试缓存功能
* 必须测试错误处理
* 必须测试异步/同步客户端

## Notes

* 所有 SDK 规格必须参考 `spec/004-client-sdks.md`
* 客户端 SDK 不包含业务逻辑
* 客户端 SDK 只负责调用 API 服务
