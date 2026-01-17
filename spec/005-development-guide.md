# Chunk Optimizer 开发指南

## 概述

本文档提供 Chunk Optimizer 项目的开发指南，包括开发环境设置、代码规范、测试要求和发布流程。

## Spec-Driven 开发原则

### 核心原则

1. **Spec 是唯一事实源（SSOT）**
   - 所有功能实现必须基于 spec
   - 不允许实现 spec 中未声明的功能
   - 如需修改功能，必须先更新 spec

2. **Scope 限制**
   - 只能在 spec 声明的 Scope 中编写代码
   - 不允许创建 spec 未声明的文件或目录
   - 如需新增文件/目录，必须先更新 spec

3. **冲突处理**
   - 如果用户请求与 spec 冲突，必须指出并拒绝实现
   - 建议用户更新 spec 后再实现

### Spec-Driven 工作流程

```
1. 阅读 spec
   ↓
2. 理解需求和约束
   ↓
3. 实现 spec 中声明的功能
   ↓
4. 编写测试验证实现
   ↓
5. 更新文档（如需要）
   ↓
6. 提交代码
```

---

## 开发环境设置

### 前置要求

- Python 3.10+
- Node.js 18+
- Poetry（Python 依赖管理）
- Docker（可选）
- Git

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/hsbreeze01/chunk-optimizer.git
cd chunk-optimizer
```

#### 2. 安装 Python 依赖

```bash
cd chunk-optimizer-service
poetry install
```

#### 3. 安装 JavaScript 依赖

```bash
cd ../chunk-optimizer-js-client
npm install
```

#### 4. 配置环境变量

```bash
cd ../chunk-optimizer-service
cp .env.example .env
```

编辑 `.env` 文件：

```env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

#### 5. 启动服务

```bash
poetry run uvicorn src.api.rest.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

---

## 项目结构

```
chunk-optimizer/
├── spec/                          # Spec 文档（唯一事实源）
│   ├── 001-core-system.md          # 核心系统规格
│   ├── 002-algorithms.md           # 算法层规格
│   ├── 003-api-layer.md           # API 层规格
│   ├── 004-client-sdks.md         # 客户端 SDK 规格
│   └── 005-development-guide.md    # 开发指南（本文件）
├── chunk-optimizer-service/         # 优化服务
│   ├── src/
│   │   ├── algorithms/            # 算法实现
│   │   ├── api/                  # API 实现
│   │   ├── config/               # 配置
│   │   ├── core/                 # 核心逻辑
│   │   ├── database/             # 数据库（Phase 2）
│   │   ├── models/               # 数据模型
│   │   └── utils/               # 工具函数
│   ├── tests/                    # 测试
│   ├── pyproject.toml           # Python 依赖
│   └── Dockerfile               # Docker 配置
├── chunk-optimizer-client/        # Python 客户端 SDK
│   ├── src/chunk_optimizer/      # SDK 实现
│   ├── tests/                   # 测试
│   └── pyproject.toml           # Python 依赖
├── chunk-optimizer-js-client/     # JavaScript/TypeScript 客户端 SDK
│   ├── src/                     # SDK 实现
│   ├── tests/                   # 测试
│   ├── package.json              # Node.js 依赖
│   └── tsconfig.json           # TypeScript 配置
├── docker-compose.yml            # Docker Compose 配置
├── .gitignore                  # Git 忽略文件
└── README.md                   # 项目说明
```

---

## 代码规范

### Python 代码规范

#### 命名规范

- **类名**: PascalCase（如 `QualityAnalyzer`）
- **函数名**: snake_case（如 `analyze_chunk`）
- **变量名**: snake_case（如 `chunk_id`）
- **常量**: UPPER_SNAKE_CASE（如 `MAX_LENGTH`）

#### 类型提示

所有函数必须包含类型提示：

```python
def analyze_chunk(
    chunk_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> OptimizationResponse:
    pass
```

#### 文档字符串

所有公共函数必须包含文档字符串：

```python
def analyze_chunk(
    chunk_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> OptimizationResponse:
    """
    Analyze a single chunk.
    
    Args:
        chunk_id: Unique identifier for the chunk
        content: Text content of the chunk
        metadata: Optional metadata
    
    Returns:
        OptimizationResponse with optimization suggestions and metrics
    
    Raises:
        ValueError: If content is empty
    """
    pass
```

#### 导入顺序

```python
# 标准库
import os
from typing import List, Optional

# 第三方库
from pydantic import BaseModel
from loguru import logger

# 本地模块
from ..algorithms.quality_analyzer import QualityAnalyzer
```

### TypeScript 代码规范

#### 命名规范

- **类名**: PascalCase（如 `ChunkOptimizerClient`）
- **函数名**: camelCase（如 `analyzeChunk`）
- **变量名**: camelCase（如 `chunkId`）
- **常量**: UPPER_SNAKE_CASE（如 `MAX_LENGTH`）
- **接口**: PascalCase（如 `Optimization`）

#### 类型定义

所有函数必须包含类型定义：

```typescript
async analyzeChunk(
  chunkId: string,
  content: string,
  metadata?: Record<string, any>
): Promise<{ optimization: Optimization; metrics: Metrics }> {
  // implementation
}
```

#### 注释

所有公共函数必须包含 JSDoc 注释：

```typescript
/**
 * Analyze a single chunk.
 * 
 * @param chunkId - Unique identifier for the chunk
 * @param content - Text content of the chunk
 * @param metadata - Optional metadata
 * @returns Optimization suggestions and metrics
 * @throws ChunkOptimizerError if analysis fails
 */
async analyzeChunk(
  chunkId: string,
  content: string,
  metadata?: Record<string, any>
): Promise<{ optimization: Optimization; metrics: Metrics }> {
  // implementation
}
```

---

## 测试要求

### 单元测试

#### 覆盖率要求

- 最低覆盖率: 80%
- 目标覆盖率: 90%

#### 测试框架

- Python: pytest
- JavaScript/TypeScript: vitest

#### 测试结构

```python
# tests/test_quality_analyzer.py
import pytest
from src.algorithms.quality_analyzer import QualityAnalyzer


class TestQualityAnalyzer:
    def test_analyze_empty_content(self):
        """Test analyzing empty content"""
        analyzer = QualityAnalyzer()
        score = analyzer.analyze("")
        assert score == 0.0
    
    def test_analyze_optimal_content(self):
        """Test analyzing optimal content"""
        analyzer = QualityAnalyzer()
        content = "This is a well-written chunk with good structure."
        score = analyzer.analyze(content)
        assert score >= 0.8
```

#### 运行测试

```bash
# Python
cd chunk-optimizer-service
poetry run pytest

# JavaScript/TypeScript
cd chunk-optimizer-js-client
npm test
```

### 集成测试

测试 API 端点：

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from src.api.rest.main import app


@pytest.mark.asyncio
async def test_analyze_chunk():
    """Test chunk analysis endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chunks/analyze",
            json={
                "chunk_id": "test-001",
                "content": "Test content"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "optimization" in data
        assert "metrics" in data
```

### 性能测试

测试响应时间：

```python
# tests/test_performance.py
import pytest
import time
from src.core.optimizer import Optimizer


@pytest.mark.asyncio
async def test_analyze_chunk_performance():
    """Test chunk analysis performance"""
    optimizer = Optimizer()
    
    start_time = time.time()
    result = await optimizer.analyze_chunk(
        chunk_id="test-001",
        content="Test content" * 100
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 0.1  # < 100ms
```

---

## Git 工作流程

### 分支策略

- `main`: 主分支，稳定代码
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支
- `hotfix/*`: 紧急修复分支

### 提交信息规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:

```
feat(algorithms): add semantic similarity detection

Implement semantic similarity detection using sentence transformers.

- Add SemanticSimilarityCalculator class
- Integrate with Optimizer
- Add unit tests

Closes #123
```

### Pull Request 流程

1. 从 `develop` 创建功能分支
2. 实现功能（基于 spec）
3. 编写测试
4. 提交代码
5. 创建 Pull Request
6. 代码审查
7. 合并到 `develop`
8. 定期合并到 `main`

---

## 发布流程

### 版本号规范

使用语义化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

### 发布步骤

#### 1. 更新版本号

```bash
# Python
cd chunk-optimizer-service
poetry version patch  # 或 minor, major

# JavaScript/TypeScript
cd chunk-optimizer-js-client
npm version patch  # 或 minor, major
```

#### 2. 更新 CHANGELOG.md

```markdown
## [0.1.1] - 2024-01-17

### Added
- Semantic similarity detection

### Fixed
- Fixed bug in phrase repetition detection

### Changed
- Improved performance of quality analyzer
```

#### 3. 创建发布标签

```bash
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

#### 4. 发布到 PyPI

```bash
cd chunk-optimizer-service
poetry build
poetry publish
```

#### 5. 发布到 npm

```bash
cd chunk-optimizer-js-client
npm publish
```

---

## 文档要求

### 代码文档

- 所有公共 API 必须有文档字符串
- 复杂逻辑必须有注释
- 使用 Sphinx 生成 Python 文档
- 使用 TypeDoc 生成 TypeScript 文档

### API 文档

- 使用 FastAPI 自动生成 OpenAPI 文档
- 访问 `/docs` 查看 Swagger UI
- 访问 `/redoc` 查看 ReDoc

### README.md

- 项目概述
- 安装说明
- 快速开始
- API 文档链接
- 贡献指南

---

## 性能优化

### 算法优化

1. **使用缓存**: 避免重复计算
2. **并行处理**: 使用 asyncio 或多线程
3. **优化算法**: 降低时间复杂度

### API 优化

1. **批量处理**: 减少网络开销
2. **连接池**: 复用 HTTP 连接
3. **压缩**: 启用 gzip 压缩

### 数据库优化（Phase 2）

1. **索引**: 添加适当的索引
2. **查询优化**: 优化 SQL 查询
3. **缓存**: 使用 Redis 缓存

---

## 安全性

### 输入验证

- 所有输入必须验证
- 使用 Pydantic 模型验证
- 防止 SQL 注入
- 防止 XSS 攻击

### 输出转义

- 所有输出必须转义
- 防止 XSS 攻击

### 认证和授权（Phase 2）

- 使用 JWT 认证
- 实现基于角色的访问控制（RBAC）
- 限流和配额

---

## 监控和日志

### 日志级别

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

### 日志格式

使用结构化日志：

```python
logger.info(
    "Chunk analyzed",
    chunk_id=chunk_id,
    quality_score=metrics.quality_score,
    response_time=response_time
)
```

### 监控指标

- 请求总数
- 响应时间
- 错误率
- 并发连接数
- 内存使用
- CPU 使用

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**问题**: `Address already in use`

**解决**:
```bash
# 检查端口占用
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

#### 2. 依赖安装失败

**问题**: `poetry install` 失败

**解决**:
```bash
# 清除缓存
poetry cache clear pypi --all

# 重新安装
poetry install
```

#### 3. 测试失败

**问题**: `pytest` 失败

**解决**:
```bash
# 运行特定测试
poetry run pytest tests/test_quality_analyzer.py::TestQualityAnalyzer::test_analyze_empty_content -v

# 查看详细输出
poetry run pytest -v -s
```

---

## 贡献指南

### 报告问题

1. 检查是否已有相同问题
2. 创建 Issue，包含：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息

### 提交代码

1. Fork 仓库
2. 创建功能分支
3. 基于 spec 实现功能
4. 编写测试
5. 提交 Pull Request
6. 等待代码审查

### 代码审查

- 检查代码是否符合规范
- 检查测试覆盖率
- 检查文档是否完整
- 检查是否遵循 spec

---

## 资源

### 文档

- [核心系统规格](001-core-system.md)
- [算法层规格](002-algorithms.md)
- [API 层规格](003-api-layer.md)
- [客户端 SDK 规格](004-client-sdks.md)

### 工具

- [Poetry](https://python-poetry.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://docs.pytest.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vitest](https://vitest.dev/)

### 社区

- GitHub Issues: https://github.com/hsbreeze01/chunk-optimizer/issues
- Discussions: https://github.com/hsbreeze01/chunk-optimizer/discussions

---

## 附录

### A. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| API_HOST | API 主机 | 0.0.0.0 |
| API_PORT | API 端口 | 8000 |
| LOG_LEVEL | 日志级别 | INFO |
| DATABASE_URL | 数据库 URL | （Phase 2） |
| REDIS_URL | Redis URL | （Phase 2） |

### B. 端口使用

| 服务 | 端口 |
|------|------|
| API | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

### C. 常用命令

```bash
# 启动服务
poetry run uvicorn src.api.rest.main:app --reload

# 运行测试
poetry run pytest

# 代码格式化
poetry run black src/
poetry run isort src/

# 类型检查
poetry run mypy src/

# 构建镜像
docker build -t chunk-optimizer .

# 启动 Docker Compose
docker-compose up -d
```

---

## 更新日志

### v0.1.0 (2024-01-17)

- 初始版本
- 核心算法实现
- RESTful API
- Python 客户端 SDK
- JavaScript/TypeScript 客户端 SDK
- Docker 支持
- Spec-driven 开发流程
