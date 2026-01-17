# Chunk Optimizer API 层规格

## 概述

本文档详细描述 Chunk Optimizer RESTful API 的端点、请求/响应格式、错误处理和认证机制。

## 基础信息

### Base URL

- 开发环境: `http://localhost:8000`
- 生产环境: 可配置（通过环境变量 `API_BASE_URL`）

### API 版本

当前版本: `v1`

版本前缀: `/api/v1`

### 认证

**当前版本**: 无需认证

**Phase 2**: JWT 认证

### 限流

**当前版本**: 无限流

**Phase 2**: 100 requests/minute per IP

---

## 端点列表

### 1. 健康检查

#### 1.1 GET /health

检查服务健康状态。

**请求**:
```http
GET /health
```

**响应** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-17T10:00:00Z"
}
```

**响应** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "error": "Service unavailable"
}
```

#### 1.2 GET /ready

检查服务是否就绪（用于 Kubernetes 健康检查）。

**请求**:
```http
GET /ready
```

**响应** (200 OK):
```json
{
  "ready": true
}
```

**响应** (503 Service Unavailable):
```json
{
  "ready": false,
  "message": "Service not ready"
}
```

---

### 2. Chunk 分析

#### 2.1 POST /api/v1/chunks/analyze

分析单个 Chunk 并返回优化建议。

**请求**:
```http
POST /api/v1/chunks/analyze
Content-Type: application/json

{
  "chunk_id": "chunk-001",
  "content": "This is a sample chunk content...",
  "metadata": {
    "source_file": "document.pdf",
    "page": 1
  }
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chunk_id | string | 是 | Chunk 唯一标识符 |
| content | string | 是 | Chunk 文本内容 |
| metadata | object | 否 | 可选的元数据 |

**响应** (200 OK):
```json
{
  "optimization": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "chunk_id": "chunk-001",
    "type": "quality",
    "priority": "medium",
    "title": "Chunk quality needs improvement",
    "description": "Quality score is 0.55, which is below the recommended threshold of 0.6",
    "suggested_action": "Review and rewrite the chunk to improve clarity, coherence, and completeness",
    "related_chunks": [],
    "created_at": "2024-01-17T10:00:00Z",
    "status": "pending"
  },
  "metrics": {
    "chunk_id": "chunk-001",
    "quality_score": 0.55,
    "redundancy_score": 0.2,
    "size_score": 0.8,
    "similarity_score": 0.1,
    "overall_score": 0.62
  }
}
```

**响应** (400 Bad Request):
```json
{
  "error": "Invalid request",
  "message": "chunk_id is required",
  "details": {
    "field": "chunk_id",
    "constraint": "required"
  }
}
```

**响应** (500 Internal Server Error):
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "request_id": "req_123456"
}
```

---

### 3. 文档分析

#### 3.1 POST /api/v1/documents/analyze

分析文档中的所有 Chunk，提供整体优化建议。

**请求**:
```http
POST /api/v1/documents/analyze
Content-Type: application/json

{
  "document_id": "doc-001",
  "chunks": [
    {
      "chunk_id": "chunk-001",
      "content": "First chunk content...",
      "metadata": {
        "source_file": "document.pdf",
        "page": 1
      }
    },
    {
      "chunk_id": "chunk-002",
      "content": "Second chunk content...",
      "metadata": {
        "source_file": "document.pdf",
        "page": 2
      }
    }
  ],
  "options": {
    "check_quality": true,
    "check_redundancy": true,
    "check_size": true,
    "check_similarity": true,
    "similarity_threshold": 0.85
  }
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| document_id | string | 是 | 文档唯一标识符 |
| chunks | array | 是 | Chunk 列表 |
| options | object | 否 | 分析选项 |

**Chunk 对象**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chunk_id | string | 是 | Chunk 唯一标识符 |
| content | string | 是 | Chunk 文本内容 |
| metadata | object | 否 | 可选的元数据 |

**Options 对象**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| check_quality | boolean | true | 是否检查质量 |
| check_redundancy | boolean | true | 是否检查冗余 |
| check_size | boolean | true | 是否检查大小 |
| check_similarity | boolean | true | 是否检查相似度 |
| similarity_threshold | float | 0.85 | 相似度阈值 |

**响应** (200 OK):
```json
{
  "document_id": "doc-001",
  "optimizations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "chunk_id": "chunk-001",
      "type": "quality",
      "priority": "medium",
      "title": "Chunk quality needs improvement",
      "description": "Quality score is 0.55, which is below the recommended threshold of 0.6",
      "suggested_action": "Review and rewrite the chunk to improve clarity, coherence, and completeness",
      "related_chunks": [],
      "created_at": "2024-01-17T10:00:00Z",
      "status": "pending"
    }
  ],
  "total": 1,
  "high_priority": 0
}
```

**响应** (400 Bad Request):
```json
{
  "error": "Invalid request",
  "message": "document_id is required",
  "details": {
    "field": "document_id",
    "constraint": "required"
  }
}
```

---

### 4. 批量分析

#### 4.1 POST /api/v1/batch/analyze

批量分析多个 Chunk，提高处理效率。

**请求**:
```http
POST /api/v1/batch/analyze
Content-Type: application/json

{
  "batch_id": "batch-001",
  "items": [
    {
      "chunk_id": "chunk-001",
      "content": "First chunk content...",
      "metadata": {
        "source_file": "document.pdf",
        "page": 1
      }
    },
    {
      "chunk_id": "chunk-002",
      "content": "Second chunk content...",
      "metadata": {
        "source_file": "document.pdf",
        "page": 2
      }
    }
  ],
  "options": {
    "check_quality": true,
    "check_redundancy": true,
    "check_size": true,
    "check_similarity": true
  }
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| batch_id | string | 是 | 批次唯一标识符 |
| items | array | 是 | Chunk 列表 |
| options | object | 否 | 分析选项 |

**响应** (200 OK):
```json
{
  "batch_id": "batch-001",
  "results": [
    {
      "item_id": "chunk-001",
      "optimization": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "chunk_id": "chunk-001",
        "type": "quality",
        "priority": "medium",
        "title": "Chunk quality needs improvement",
        "description": "Quality score is 0.55, which is below the recommended threshold of 0.6",
        "suggested_action": "Review and rewrite the chunk to improve clarity, coherence, and completeness",
        "related_chunks": [],
        "created_at": "2024-01-17T10:00:00Z",
        "status": "pending"
      },
      "metrics": {
        "chunk_id": "chunk-001",
        "quality_score": 0.55,
        "redundancy_score": 0.2,
        "size_score": 0.8,
        "similarity_score": 0.1,
        "overall_score": 0.62
      }
    }
  ],
  "processed": 2,
  "total": 2,
  "failed": 0
}
```

**响应** (400 Bad Request):
```json
{
  "error": "Invalid request",
  "message": "batch_id is required",
  "details": {
    "field": "batch_id",
    "constraint": "required"
  }
}
```

---

### 5. 相似度计算

#### 5.1 POST /api/v1/similarity/calculate

计算两个 Chunk 之间的相似度。

**请求**:
```http
POST /api/v1/similarity/calculate
Content-Type: application/json

{
  "content1": "This is the first chunk content...",
  "content2": "This is the second chunk content..."
}
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content1 | string | 是 | 第一个 Chunk 的内容 |
| content2 | string | 是 | 第二个 Chunk 的内容 |

**响应** (200 OK):
```json
{
  "similarity_score": 0.35,
  "method": "jaccard",
  "details": {
    "intersection": 5,
    "union": 14
  }
}
```

**响应** (400 Bad Request):
```json
{
  "error": "Invalid request",
  "message": "content1 and content2 are required"
}
```

---

## 数据模型

### Optimization（优化建议）

```typescript
interface Optimization {
  id: string;                    // UUID
  chunk_id: string;              // Chunk ID
  type: 'quality' | 'redundancy' | 'size' | 'similarity' | 'info';
  priority: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  suggested_action: string;
  related_chunks: string[];      // 相关 Chunk ID 列表
  created_at: string;            // ISO8601
  status: 'pending' | 'applied' | 'ignored';
}
```

### Metrics（指标）

```typescript
interface Metrics {
  chunk_id: string;
  quality_score: number;         // 0-1
  redundancy_score: number;       // 0-1
  size_score: number;            // 0-1
  similarity_score: number;       // 0-1
  overall_score: number;          // 0-1
}
```

### Chunk（Chunk 对象）

```typescript
interface Chunk {
  chunk_id: string;
  content: string;
  metadata?: Record<string, any>;
}
```

### AnalysisOptions（分析选项）

```typescript
interface AnalysisOptions {
  check_quality?: boolean;
  check_redundancy?: boolean;
  check_size?: boolean;
  check_similarity?: boolean;
  similarity_threshold?: number;
}
```

---

## 错误处理

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "constraint": "constraint_name"
  },
  "request_id": "req_123456"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 429 | 请求过多（限流） |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

### 错误类型

| 错误类型 | 状态码 | 说明 |
|---------|--------|------|
| InvalidRequest | 400 | 请求参数错误 |
| ValidationError | 422 | 数据验证失败 |
| NotFound | 404 | 资源不存在 |
| RateLimitExceeded | 429 | 超过限流阈值 |
| InternalServerError | 500 | 服务器内部错误 |
| ServiceUnavailable | 503 | 服务不可用 |

---

## 请求头

### 标准请求头

| 请求头 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Content-Type | string | 是 | 必须为 `application/json` |
| Accept | string | 否 | 默认为 `application/json` |
| User-Agent | string | 否 | 客户端标识 |
| X-Request-ID | string | 否 | 请求追踪 ID |
| Authorization | string | 否 | Phase 2: JWT Token |

### 响应头

| 响应头 | 类型 | 说明 |
|--------|------|------|
| Content-Type | string | 响应内容类型 |
| X-Request-ID | string | 请求追踪 ID |
| X-Response-Time | number | 响应时间（毫秒） |
| X-Rate-Limit-Remaining | number | 剩余请求次数（Phase 2） |
| X-Rate-Limit-Reset | number | 限流重置时间（Phase 2） |

---

## 分页

### 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| per_page | integer | 20 | 每页数量（最大 100） |

### 分页响应

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

## 排序

### 排序参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| sort_by | string | created_at | 排序字段 |
| order | string | desc | 排序方向（asc/desc） |

### 支持的排序字段

- `created_at`: 创建时间
- `priority`: 优先级
- `overall_score`: 综合分数

---

## 过滤

### 过滤参数

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | 优化类型（quality/redundancy/size/similarity） |
| priority | string | 优先级（low/medium/high） |
| status | string | 状态（pending/applied/ignored） |
| min_score | number | 最小分数 |
| max_score | number | 最大分数 |
| date_from | string | 开始日期（ISO8601） |
| date_to | string | 结束日期（ISO8601） |

---

## 认证（Phase 2）

### JWT 认证

**获取 Token**:
```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**使用 Token**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 限流（Phase 2）

### 限流规则

- 每个用户/IP: 100 requests/minute
- 每个用户/IP: 1000 requests/hour

### 限流响应

```http
HTTP/1.1 429 Too Many Requests
X-Rate-Limit-Remaining: 0
X-Rate-Limit-Reset: 1705483200
Retry-After: 60

{
  "error": "RateLimitExceeded",
  "message": "Too many requests",
  "retry_after": 60
}
```

---

## 性能要求

### 响应时间

| 端点 | 目标响应时间 |
|------|-------------|
| GET /health | < 10ms |
| POST /api/v1/chunks/analyze | < 100ms |
| POST /api/v1/documents/analyze (10 chunks) | < 500ms |
| POST /api/v1/batch/analyze (100 chunks) | < 2s |

### 吞吐量

- 单实例: > 100 requests/second
- 水平扩展: 支持多实例负载均衡

---

## 安全性

### 输入验证

- 所有输入必须经过验证
- 防止 SQL 注入
- 防止 XSS 攻击
- 防止 CSRF 攻击

### 输出转义

- 所有输出必须转义
- 防止 XSS 攻击

### HTTPS

- 生产环境必须使用 HTTPS
- 开发环境可以使用 HTTP

### CORS

- 允许跨域请求（可配置）
- 默认允许所有来源（开发环境）
- 生产环境需要配置允许的来源

---

## 版本控制

### API 版本策略

- 使用 URL 路径版本控制: `/api/v1/`
- 主版本号变更时创建新版本: `/api/v2/`
- 旧版本至少维护 6 个月

### 版本变更通知

- 提前 3 个月通知版本废弃
- 在响应头中添加废弃警告: `X-API-Deprecated: true`
- 在文档中明确标注废弃版本

---

## 监控和日志

### 日志级别

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

### 日志格式

```json
{
  "timestamp": "2024-01-17T10:00:00Z",
  "level": "INFO",
  "message": "Request received",
  "request_id": "req_123456",
  "method": "POST",
  "path": "/api/v1/chunks/analyze",
  "status_code": 200,
  "response_time": 50
}
```

### 监控指标

- 请求总数
- 响应时间
- 错误率
- 并发连接数
- 内存使用
- CPU 使用

---

## 测试

### 单元测试

- 覆盖所有端点
- 测试正常场景
- 测试异常场景
- 测试边界条件

### 集成测试

- 测试端到端流程
- 测试错误处理
- 测试认证和授权（Phase 2）
- 测试限流（Phase 2）

### 性能测试

- 响应时间测试
- 并发测试
- 压力测试

---

## 文档

### Swagger/OpenAPI

- 自动生成 API 文档
- 访问地址: `/docs`
- 交互式 API 测试

### 示例代码

- Python 客户端示例
- JavaScript/TypeScript 客户端示例
- cURL 示例

---

## 最佳实践

### 客户端实现

1. 使用适当的 HTTP 客户端库
2. 实现重试机制（指数退避）
3. 实现超时处理
4. 实现错误处理
5. 实现日志记录

### 请求优化

1. 批量请求代替单个请求
2. 使用缓存减少重复请求
3. 压缩请求体（如果很大）
4. 使用连接池

### 错误处理

1. 检查 HTTP 状态码
2. 解析错误响应
3. 实现重试逻辑（对于可重试的错误）
4. 记录错误日志

---

## 未来扩展

### Phase 2

- JWT 认证
- 限流和配额
- WebSocket 实时推送
- 数据库持久化

### Phase 3

- gRPC API
- GraphQL API
- 高级过滤和搜索
- 自定义分析选项
