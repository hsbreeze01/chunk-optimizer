# Chunk Optimizer

一个用于优化 RAG（检索增强生成）系统中文档 Chunk 的独立服务。

## 项目结构

```
chunk-optimizer/
├── chunk-optimizer-service/      # 优化服务（Python + FastAPI）
├── chunk-optimizer-client/       # Python 客户端 SDK
├── chunk-optimizer-js-client/    # JavaScript/TypeScript 客户端 SDK
└── README.md
```

## 功能特性

### 优化服务

- **质量分析**：评估 Chunk 的内容质量
- **重复检测**：识别重复和冗余内容
- **大小优化**：分析 Chunk 大小是否合适
- **相似度计算**：检测高度相似的内容

### 客户端 SDK

- Python SDK（同步和异步）
- JavaScript/TypeScript SDK
- 内置缓存支持
- 完整的错误处理

## 快速开始

### 安装服务

```bash
cd chunk-optimizer-service
poetry install
cp .env.example .env
```

### 启动服务

```bash
poetry run uvicorn src.api.rest.main:app --reload --host 0.0.0.0 --port 8000
```

### 使用 Python 客户端

```python
from chunk_optimizer import ChunkOptimizerClient

client = ChunkOptimizerClient(
    api_key="your-api-key",
    base_url="http://localhost:8000"
)

optimization, metrics = await client.analyze_chunk(
    chunk_id="chunk-1",
    content="Your chunk content here"
)

print(f"Quality score: {metrics.quality_score}")
print(f"Optimization: {optimization.title}")
```

### 使用 JavaScript 客户端

```typescript
import { ChunkOptimizerClient } from 'chunk-optimizer-js-client';

const client = new ChunkOptimizerClient({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:8000'
});

const result = await client.analyzeChunk(
  'chunk-1',
  'Your chunk content here'
);

console.log(`Quality score: ${result.metrics.quality_score}`);
console.log(`Optimization: ${result.optimization.title}`);
```

## API 文档

启动服务后，访问 `http://localhost:8000/docs` 查看完整的 API 文档。

## 开发计划

- [ ] 添加 gRPC 支持
- [ ] 添加 WebSocket 实时推送
- [ ] 实现数据库持久化
- [ ] 添加认证和授权
- [ ] 实现限流和配额
- [ ] 添加监控和日志

## 许可证

MIT License
