# System Specification

## Responsibility

定义整个工程的最高约束与开发范式。

## Scope

* 所有 `chunk-optimizer-service/src/` 下代码
* 所有 `chunk-optimizer-client/src/` 下代码
* 所有 `chunk-optimizer-js-client/src/` 下代码
* 所有 Code Agent 行为

## Global Rules

* spec 是唯一事实源（SSOT）
* src 中的任何目录，必须能映射到 spec
* 不允许 spec 外新增模块
* 所有实现必须基于 spec 声明的内容
* 不允许创建 spec 未声明的文件或目录

## Architecture

### Service Layer (chunk-optimizer-service)

```
chunk-optimizer-service/src/
├── algorithms/          # 算法层
│   ├── quality_analyzer.py
│   ├── redundancy_detector.py
│   ├── size_analyzer.py
│   └── similarity_calculator.py
├── api/               # API 层
│   └── rest/
│       ├── main.py
│       ├── schemas/
│       └── middleware/
├── core/              # 核心层
│   └── optimizer.py
├── config/            # 配置
│   └── settings.py
├── models/            # 数据模型
│   └── schemas.py
└── utils/             # 工具函数
```

### Client SDK Layer (chunk-optimizer-client)

```
chunk-optimizer-client/src/chunk_optimizer/
├── client.py          # 异步客户端
├── sync_client.py     # 同步客户端
├── models.py          # 数据模型
└── exceptions.py      # 异常定义
```

### Client SDK Layer (chunk-optimizer-js-client)

```
chunk-optimizer-js-client/src/
├── client.ts         # 客户端实现
├── models.ts        # 数据模型
└── exceptions.ts    # 异常定义
```

## Layer Boundaries

### Algorithms Layer

* **Responsibility**: 实现核心分析算法
* **Scope**: `chunk-optimizer-service/src/algorithms/`
* **Allowed Files**:
  * `quality_analyzer.py`
  * `redundancy_detector.py`
  * `size_analyzer.py`
  * `similarity_calculator.py`
* **Dependencies**: 仅允许 Python 标准库
* **Forbidden**:
  * 访问 infrastructure
  * 调用第三方 SDK
  * IO / 网络 / 数据库

### API Layer

* **Responsibility**: 提供 RESTful API 接口
* **Scope**: `chunk-optimizer-service/src/api/`
* **Allowed Files**:
  * `main.py`
  * `schemas/` 目录下的文件
  * `middleware/` 目录下的文件
* **Dependencies**: core, algorithms
* **Forbidden**:
  * 直接访问数据库
  * 直接调用第三方 API
  * 包含业务规则

### Core Layer

* **Responsibility**: 编排算法，生成优化建议
* **Scope**: `chunk-optimizer-service/src/core/`
* **Allowed Files**:
  * `optimizer.py`
* **Dependencies**: algorithms
* **Forbidden**:
  * 直接访问数据库
  * 直接调用第三方 API

### Client SDK Layer

* **Responsibility**: 提供客户端 SDK
* **Scope**: `chunk-optimizer-client/src/` 或 `chunk-optimizer-js-client/src/`
* **Allowed Files**:
  * `client.py` / `client.ts`
  * `sync_client.py` (Python only)
  * `models.py` / `models.ts`
  * `exceptions.py` / `exceptions.ts`
* **Dependencies**: httpx (Python), fetch (TypeScript)
* **Forbidden**:
  * 包含业务规则
  * 直接访问数据库

## Forbidden

* 在 src 中创建未声明的目录
* 在未修改 spec 的情况下新增文件
* 实现 spec 中未声明的功能
* 跨越层边界
* 修改 spec 文件（需要明确的人类指令）

## Notes

* `docs/` 仅用于解释，不具备约束力
* `spec/` 目录下的所有 `.md` 文件都是只读的
* 任何 spec 变更需要明确的人类指令
* 失败优于错误执行
