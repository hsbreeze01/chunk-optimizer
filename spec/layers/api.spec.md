# API Layer Specification

## Responsibility

* 提供 RESTful API 接口
* 处理 HTTP 请求和响应
* 参数解析和验证
* 结果返回和错误处理

## Scope

`chunk-optimizer-service/src/api/`

## Allowed Files

* `main.py` - FastAPI 应用入口
* `schemas/` 目录下的文件 - 请求/响应模型
* `middleware/` 目录下的文件 - 中间件

## Dependencies

* `core` - 核心优化引擎
* `algorithms` - 算法层（通过 core）
* `fastapi` - Web 框架
* `pydantic` - 数据验证
* `loguru` - 日志

## Forbidden

* 直接访问数据库
* 直接调用第三方 API
* 包含业务规则（交由 core 层）
* 跨越层边界直接调用 algorithms

## Implementation Requirements

### Endpoints

必须实现以下端点（参考 `spec/003-api-layer.md`）：

1. **GET /health** - 健康检查
2. **GET /ready** - 就绪检查
3. **POST /api/v1/chunks/analyze** - 分析单个 Chunk
4. **POST /api/v1/documents/analyze** - 分析文档
5. **POST /api/v1/batch/analyze** - 批量分析
6. **POST /api/v1/similarity/calculate** - 计算相似度

### Request/Response Models

所有请求和响应模型必须使用 Pydantic 定义：

* `AnalyzeChunkRequest` - Chunk 分析请求
* `OptimizationResponse` - 优化响应
* `Metrics` - 指标
* `AnalyzeDocumentRequest` - 文档分析请求
* `DocumentAnalysisResponse` - 文档分析响应
* `BatchAnalyzeRequest` - 批量分析请求
* `BatchAnalysisResponse` - 批量分析响应
* `SimilarityRequest` - 相似度计算请求
* `SimilarityResponse` - 相似度计算响应

### Error Handling

所有错误必须遵循统一格式：

```python
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "constraint": "constraint_name"
  },
  "request_id": "req_123456"
}
```

### Middleware

必须实现以下中间件：

* **CORS Middleware** - 跨域请求支持
* **Logging Middleware** - 请求日志记录
* **Error Handler Middleware** - 统一错误处理

### Performance Requirements

* GET /health: < 10ms
* POST /api/v1/chunks/analyze: < 100ms
* POST /api/v1/documents/analyze (10 chunks): < 500ms
* POST /api/v1/batch/analyze (100 chunks): < 2s

## Testing Requirements

* 所有端点必须有集成测试
* 测试正常场景
* 测试异常场景
* 测试边界条件
* 测试性能要求

## Notes

* API 层只负责"怎么做"，不负责"做什么"
* 业务逻辑必须委托给 core 层
* 所有 API 规格必须参考 `spec/003-api-layer.md`
* 使用 FastAPI 自动生成 OpenAPI 文档
