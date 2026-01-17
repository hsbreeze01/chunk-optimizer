# Chunk Optimizer 核心系统规格

## 概述

Chunk Optimizer 是一个用于优化 RAG（检索增强生成）系统中文档 Chunk 的独立服务。该服务提供质量分析、重复检测、大小优化和相似度计算等功能，并通过 RESTful API 和客户端 SDK 暴露给外部使用。

## 目标

1. 提高文档 Chunk 的质量和检索效果
2. 减少冗余和重复内容
3. 优化 Chunk 大小以提高检索精度
4. 检测高度相似的内容以避免重复索引
5. 提供易于集成的客户端 SDK（Python 和 JavaScript/TypeScript）

## 范围

### 包含

- Chunk 质量分析算法
- Chunk 重复检测算法
- Chunk 大小分析算法
- Chunk 相似度计算算法
- RESTful API 服务
- Python 客户端 SDK（异步和同步）
- JavaScript/TypeScript 客户端 SDK
- Docker 部署支持

### 不包含

- 文档分块算法（由上游系统负责）
- 向量数据库集成（由上游系统负责）
- 用户认证和授权管理（Phase 2）
- 数据持久化存储（Phase 2）
- gRPC API（Phase 2）
- WebSocket 实时推送（Phase 2）

## 功能需求

### 1. 质量分析

**优先级**: P0（必须）

**描述**: 评估 Chunk 的内容质量，从多个维度给出评分和建议。

**输入**:
- `chunk_id`: string - Chunk 唯一标识符
- `content`: string - Chunk 文本内容
- `metadata`: object - 可选的元数据

**输出**:
- `quality_score`: float (0-1) - 质量分数
- `optimization`: object - 优化建议（如果质量低于阈值）

**评分维度**:
1. 长度分析 (40%)
   - 最优范围: 300-1000 字符
   - 最小值: 50 字符
   - 最大值: 2000 字符

2. 句子结构分析 (20%)
   - 最优句子长度: 10-25 词
   - 检测过短或过长的句子

3. 词汇多样性分析 (20%)
   - 最优多样性: >= 60%
   - 检测词汇丰富度

4. 连贯性分析 (20%)
   - 检测逻辑连接词的使用
   - 支持中英文连接词

**阈值**:
- 质量分数 < 0.4: 高优先级优化建议
- 质量分数 < 0.6: 中优先级优化建议
- 质量分数 >= 0.6: 无需优化

### 2. 重复检测

**优先级**: P0（必须）

**描述**: 检测 Chunk 内部的重复内容，包括短语、句子和单词重复。

**输入**:
- `chunk_id`: string - Chunk 唯一标识符
- `content`: string - Chunk 文本内容

**输出**:
- `redundancy_score`: float (0-1) - 冗余分数
- `optimization`: object - 优化建议（如果冗余超过阈值）

**检测维度**:
1. 短语重复 (40%)
   - 短语长度: 3-8 词
   - 重复阈值: >= 2 次

2. 句子重复 (30%)
   - 重复阈值: >= 2 次
   - 检测完全相同的句子

3. 单词重复 (30%)
   - 最小词数: 10 词
   - 词汇多样性阈值:
     - >= 70%: 无冗余
     - >= 50%: 轻度冗余
     - >= 30%: 中度冗余
     - < 30%: 重度冗余

**阈值**:
- 冗余分数 > 0.7: 高优先级优化建议
- 冗余分数 > 0.5: 中优先级优化建议
- 冗余分数 <= 0.5: 无需优化

### 3. 大小分析

**优先级**: P0（必须）

**描述**: 评估 Chunk 长度是否在合理范围内，提供分段建议。

**输入**:
- `chunk_id`: string - Chunk 唯一标识符
- `content`: string - Chunk 文本内容

**输出**:
- `size_score`: float (0-1) - 大小分数
- `optimization`: object - 优化建议（如果大小不理想）

**评分标准**:
- 最优范围: 300-1000 字符
- 最小值: 50 字符
- 最大值: 2000 字符
- 评分函数: 连续线性插值，无跳跃

**阈值**:
- 大小分数 < 0.5: 中优先级优化建议
- 大小分数 >= 0.5: 无需优化

### 4. 相似度计算

**优先级**: P0（必须）

**描述**: 计算 Chunk 内部的相似度（内部重复）和两个 Chunk 之间的相似度（跨 Chunk 重复）。

**输入**:
- `chunk_id`: string - Chunk 唯一标识符
- `content`: string - Chunk 文本内容
- `other_content`: string (可选) - 另一个 Chunk 的内容

**输出**:
- `similarity_score`: float (0-1) - 相似度分数
- `optimization`: object - 优化建议（如果相似度过高）

**计算方法**:
1. 内部相似度 (默认)
   - 过滤停用词（50+ 个中英文词）
   - 统计重复单词
   - 最大重复比例: 30%

2. Jaccard 相似度 (跨 Chunk)
   - 公式: |A ∩ B| / |A ∪ B|
   - 范围: [0, 1]

**阈值**:
- 相似度分数 > 0.85: 高优先级优化建议
- 相似度分数 <= 0.85: 无需优化

### 5. 优化引擎

**优先级**: P0（必须）

**描述**: 整合所有分析算法，生成综合优化建议。

**输入**:
- `chunk_id`: string - Chunk 唯一标识符
- `content`: string - Chunk 文本内容
- `options`: object - 分析选项

**输出**:
- `metrics`: object - 包含所有维度的分数
- `optimizations`: array - 优化建议列表
- `overall_score`: float (0-1) - 综合分数

**综合评分权重**:
- 质量分数: 40%
- (1 - 冗余分数): 30%
- 大小分数: 20%
- (1 - 相似度分数): 10%

**分析选项**:
- `check_quality`: boolean (默认: true) - 是否检查质量
- `check_redundancy`: boolean (默认: true) - 是否检查冗余
- `check_size`: boolean (默认: true) - 是否检查大小
- `check_similarity`: boolean (默认: true) - 是否检查相似度
- `similarity_threshold`: float (默认: 0.85) - 相似度阈值

### 6. 批量分析

**优先级**: P1（重要）

**描述**: 支持批量分析多个 Chunk，提高处理效率。

**输入**:
- `batch_id`: string - 批次唯一标识符
- `items`: array - Chunk 列表
- `options`: object - 分析选项

**输出**:
- `batch_id`: string - 批次标识符
- `processed`: integer - 已处理数量
- `total`: integer - 总数量
- `optimizations`: array - 优化建议列表

### 7. 文档分析

**优先级**: P1（重要）

**描述**: 分析文档中的所有 Chunk，提供整体优化建议。

**输入**:
- `document_id`: string - 文档唯一标识符
- `chunks`: array - Chunk 列表
- `options`: object - 分析选项

**输出**:
- `document_id`: string - 文档标识符
- `optimizations`: array - 优化建议列表
- `total`: integer - 总优化建议数
- `high_priority`: integer - 高优先级建议数

## API 需求

### RESTful API

**基础 URL**: `http://localhost:8000`（可配置）

**认证**: Phase 2（当前版本不需要）

**限流**: Phase 2（当前版本不需要）

#### 端点

1. `GET /health` - 健康检查
2. `GET /ready` - 就绪检查
3. `POST /api/v1/chunks/analyze` - 分析单个 Chunk
4. `POST /api/v1/documents/analyze` - 分析文档的所有 Chunk
5. `POST /api/v1/batch/analyze` - 批量分析

#### 响应格式

所有 API 响应使用 JSON 格式，遵循以下结构：

```json
{
  "optimization": {
    "id": "uuid",
    "chunk_id": "string",
    "type": "string",
    "priority": "low|medium|high",
    "title": "string",
    "description": "string",
    "suggested_action": "string",
    "related_chunks": ["string"],
    "created_at": "ISO8601",
    "status": "pending|applied|ignored"
  },
  "metrics": {
    "chunk_id": "string",
    "quality_score": 0.0-1.0,
    "redundancy_score": 0.0-1.0,
    "size_score": 0.0-1.0,
    "similarity_score": 0.0-1.0,
    "overall_score": 0.0-1.0
  }
}
```

## 客户端 SDK 需求

### Python SDK

**包名**: `chunk-optimizer-client`

**版本**: 0.1.0

**依赖**:
- Python >= 3.10
- pydantic >= 2.5.0
- httpx >= 0.25.2
- aiohttp >= 3.9.1

**功能**:
- 异步客户端 (`ChunkOptimizerClient`)
- 同步客户端包装器 (`SyncChunkOptimizerClient`)
- 内置缓存支持（可选，默认启用）
- 完整的错误处理
- 类型提示支持

**API**:
```python
class ChunkOptimizerClient:
    async def analyze_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optimization, Metrics]:
        pass
    
    async def analyze_document(
        self,
        document_id: str,
        chunks: List[Chunk],
        options: Optional[OptimizationOptions] = None
    ) -> List[Optimization]:
        pass
    
    async def analyze_batch(
        self,
        items: List[BatchItem],
        options: Optional[OptimizationOptions] = None
    ) -> BatchResult:
        pass
    
    async def close(self) -> None:
        pass
```

### JavaScript/TypeScript SDK

**包名**: `chunk-optimizer-js-client`

**版本**: 0.1.0

**依赖**:
- TypeScript >= 5.0
- Node.js >= 18

**功能**:
- TypeScript 客户端
- 内置缓存支持（可选，默认启用）
- 完整的错误处理
- 类型定义完整

**API**:
```typescript
class ChunkOptimizerClient {
  constructor(config: ChunkOptimizerConfig);
  
  async analyzeChunk(
    chunkId: string,
    content: string,
    metadata?: Record<string, any>
  ): Promise<{ optimization: Optimization; metrics: Metrics }>;
  
  async analyzeDocument(
    documentId: string,
    chunks: Chunk[],
    options?: OptimizationOptions
  ): Promise<{ optimizations: Optimization[]; total: number; high_priority: number }>;
  
  async analyzeBatch(
    items: Chunk[],
    options?: OptimizationOptions
  ): Promise<BatchResult>;
  
  clearCache(): void;
}
```

## 性能要求

### 响应时间

- 单 Chunk 分析: < 100ms
- 文档分析（10 Chunks）: < 500ms
- 批量分析（100 Chunks）: < 2s

### 吞吐量

- 单实例: > 100 requests/second
- 水平扩展: 支持多实例负载均衡

### 资源使用

- 内存: < 512MB per instance
- CPU: < 50% per request (单核）

## 部署要求

### 开发环境

- Python 3.10+
- Poetry（依赖管理）
- Docker（可选）

### 生产环境

- Docker + Docker Compose
- PostgreSQL 15+（Phase 2）
- Redis 7+（Phase 2）
- Nginx（反向代理，可选）

## 测试要求

### 单元测试

- 覆盖率: >= 80%
- 框架: pytest

### 集成测试

- API 端到端测试
- 客户端 SDK 集成测试

### 性能测试

- 响应时间测试
- 并发测试
- 压力测试

## 交付物

### 代码

- chunk-optimizer-service（Python + FastAPI）
- chunk-optimizer-client（Python SDK）
- chunk-optimizer-js-client（TypeScript SDK）

### 文档

- API 文档（Swagger/OpenAPI）
- README.md
- 开发指南

### 配置

- Dockerfile
- docker-compose.yml
- .env.example

## 版本计划

### v0.1.0（当前版本）

- ✅ 核心算法实现
- ✅ RESTful API
- ✅ Python 客户端 SDK
- ✅ JavaScript/TypeScript 客户端 SDK
- ✅ Docker 支持

### v0.2.0（计划中）

- ⏳ 数据库持久化
- ⏳ 认证和授权
- ⏳ 限流和配额
- ⏳ gRPC API

### v0.3.0（计划中）

- ⏳ WebSocket 实时推送
- ⏳ 机器学习质量预测
- ⏳ 语义相似度检测
- ⏳ 多语言支持

## 非功能性需求

### 安全性

- 输入验证（防止注入攻击）
- 输出转义（防止 XSS）
- 速率限制（Phase 2）
- HTTPS 支持（生产环境）

### 可维护性

- 模块化设计
- 清晰的代码结构
- 完整的类型提示
- 单元测试覆盖

### 可扩展性

- 水平扩展支持
- 配置驱动
- 插件化算法（未来）

### 可观测性

- 结构化日志
- 性能指标
- 健康检查端点
- 错误追踪（Phase 2）
