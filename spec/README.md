# Chunk Optimizer Spec 文档

## 概述

本目录包含 Chunk Optimizer 项目的所有规格文档（Spec）。这些文档是项目的**唯一事实源（SSOT）**，所有开发工作必须基于这些规格文档进行。

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

## 文档结构

### Base 规约

这些文档定义了项目的最高约束和开发范式：

| 文件 | 描述 | 优先级 |
|------|------|---------|
| [AGENT.md](../AGENT.md) | Agent 行为规约，定义 AI Agent 必须遵守的规则 | 最高 |
| [system.spec.md](system.spec.md) | 系统规格，定义整个工程的最高约束与开发范式 | 最高 |

### 层级规约

这些文档定义了各个层的职责、范围和约束：

| 文件 | 描述 | 适用对象 |
|------|------|---------|
| [algorithms.spec.md](layers/algorithms.spec.md) | 算法层规格 | 算法开发者 |
| [api.spec.md](layers/api.spec.md) | API 层规格 | API 开发者 |
| [core.spec.md](layers/core.spec.md) | 核心层规格 | 核心开发者 |
| [client.spec.md](layers/client.spec.md) | 客户端 SDK 层规格 | SDK 开发者 |

### 功能规格

这些文档详细描述了各个功能模块的实现细节：

| 文件 | 描述 | 适用对象 |
|------|------|---------|
| [001-core-system.md](001-core-system.md) | 核心系统规格 | 所有开发者 |
| [002-algorithms.md](002-algorithms.md) | 算法层详细规格 | 算法开发者 |
| [003-api-layer.md](003-api-layer.md) | API 层详细规格 | API 开发者 |
| [004-client-sdks.md](004-client-sdks.md) | 客户端 SDK 详细规格 | SDK 开发者 |
| [005-development-guide.md](005-development-guide.md) | 开发指南 | 所有开发者 |

## 优先级和权威性

### 权威性优先级

Agent 必须遵守以下优先级顺序（无例外）：

1. `AGENT.md` (最高优先级)
2. `spec/system.spec.md`
3. `spec/layers/*.spec.md`
4. `spec/modules/*.spec.md` (如有)
5. `spec/00X-*.md` (功能规格)
6. 现有源代码

### 冲突处理

如果发现任何冲突：

* **立即停止**
* **报告冲突**
* **不要猜测或自主解决**

### 只读规则

以下文件和目录是**严格只读**的：

* `spec/**/*.spec.md`
* `spec/**/*.md`
* `AGENT.md`

Agent 必须**不**：

* 修改 spec 文件
* 重写 spec 措辞
* "修复"或"改进" spec 定义

任何 spec 变更需要**明确的人类指令**。

## 如何使用 Spec 文档

### 开始新功能开发

1. **阅读相关 spec 文档**
   - 首先阅读 [AGENT.md](../AGENT.md) 了解 Agent 行为规约
   - 阅读 [system.spec.md](system.spec.md) 了解系统约束
   - 阅读相关层级的 spec 文档
   - 阅读功能规格文档

2. **理解需求和约束**
   - 明确功能目标
   - 了解性能要求
   - 注意边界条件

3. **实现功能**
   - 按照 spec 中的描述实现
   - 遵循代码规范
   - 不超出 spec 声明的 Scope

4. **编写测试**
   - 单元测试
   - 集成测试
   - 性能测试（如需要）

5. **更新文档**
   - API 文档（自动生成）
   - README（如需要）

6. **提交代码**
   - 遵循 Git 提交规范
   - 创建 Pull Request
   - 引用相关 spec

### 修复 Bug

1. **定位问题**
   - 阅读相关 spec
   - 理解预期行为

2. **修复问题**
   - 保持与 spec 一致
   - 不改变 spec 声明的行为

3. **添加测试**
   - 添加回归测试
   - 确保问题不再出现

4. **提交代码**
   - 在提交信息中引用 spec

### 优化性能

1. **阅读性能要求**
   - 查看 spec 中的性能要求
   - 了解目标响应时间

2. **分析瓶颈**
   - 使用性能分析工具
   - 找出性能瓶颈

3. **优化实现**
   - 按照 spec 中的优化建议
   - 不改变功能行为

4. **验证优化**
   - 运行性能测试
   - 确保达到性能目标

## 层级架构

### 系统架构

```
chunk-optimizer/
├── AGENT.md                    # Agent 行为规约
├── spec/
│   ├── system.spec.md           # 系统规格
│   ├── layers/                 # 层级规约
│   │   ├── algorithms.spec.md   # 算法层
│   │   ├── api.spec.md         # API 层
│   │   ├── core.spec.md        # 核心层
│   │   └── client.spec.md     # 客户端 SDK 层
│   ├── 001-core-system.md       # 核心系统规格
│   ├── 002-algorithms.md        # 算法层详细规格
│   ├── 003-api-layer.md        # API 层详细规格
│   ├── 004-client-sdks.md      # 客户端 SDK 详细规格
│   ├── 005-development-guide.md # 开发指南
│   └── README.md              # 本文件
├── chunk-optimizer-service/      # 优化服务
│   └── src/
│       ├── algorithms/          # 算法层
│       ├── api/               # API 层
│       ├── core/              # 核心层
│       ├── config/            # 配置
│       ├── models/            # 数据模型
│       └── utils/             # 工具函数
├── chunk-optimizer-client/       # Python 客户端 SDK
│   └── src/chunk_optimizer/
└── chunk-optimizer-js-client/    # JavaScript/TypeScript 客户端 SDK
    └── src/
```

### 层级职责

#### Algorithms Layer

* **职责**: 实现核心分析算法
* **范围**: `chunk-optimizer-service/src/algorithms/`
* **依赖**: 仅允许 Python 标准库
* **禁止**: 访问 infrastructure、调用第三方 SDK、IO/网络/数据库

#### API Layer

* **职责**: 提供 RESTful API 接口
* **范围**: `chunk-optimizer-service/src/api/`
* **依赖**: core, algorithms
* **禁止**: 直接访问数据库、直接调用第三方 API、包含业务规则

#### Core Layer

* **职责**: 编排算法，生成优化建议
* **范围**: `chunk-optimizer-service/src/core/`
* **依赖**: algorithms
* **禁止**: 直接访问数据库、直接调用第三方 API

#### Client SDK Layer

* **职责**: 提供客户端 SDK
* **范围**: `chunk-optimizer-client/src/` 或 `chunk-optimizer-js-client/src/`
* **依赖**: httpx (Python), fetch (TypeScript)
* **禁止**: 包含业务规则、直接访问数据库

## 常见问题

### Q: 可以不遵循 spec 实现功能吗？

**A**: 不可以。spec 是唯一事实源，所有实现必须基于 spec。如果需要实现 spec 中未声明的功能，必须先更新 spec。

### Q: 发现 spec 有错误怎么办？

**A**: 立即创建 Issue 说明问题，然后提交 Pull Request 修复 spec。修复 spec 后，再更新相关实现。

### Q: 性能达不到 spec 要求怎么办？

**A**: 按照 spec 中的性能优化建议进行优化。如果仍然无法达到要求，需要更新 spec 中的性能指标。

### Q: 可以跳过测试直接提交代码吗？

**A**: 不可以。spec 明确要求测试覆盖率 >= 80%。所有代码必须通过测试才能提交。

### Q: 如何判断功能是否在 spec 的 Scope 中？

**A**: 阅读相关 spec 文档，查看功能需求部分。如果功能未在 spec 中声明，则不在 Scope 中。

### Q: Agent 可以修改 spec 文件吗？

**A**: 不可以。spec 文件是严格只读的。任何 spec 变更需要明确的人类指令。

### Q: 如果用户请求与 spec 冲突怎么办？

**A**: 立即停止，报告冲突，建议用户更新 spec 后再实现。不要猜测或自主解决冲突。

## 贡献指南

### 报告 Spec 问题

1. 检查是否已有相同问题
2. 创建 Issue，包含：
   - 问题描述
   - 建议的修复方案
   - 影响范围

### 提交 Spec 更新

1. Fork 仓库
2. 创建功能分支
3. 更新 spec 文档
4. 提交 Pull Request
5. 等待代码审查

### 代码审查要点

- 检查是否符合 Spec-Driven 原则
- 检查是否在 Scope 内
- 检查格式是否一致
- 检查是否清晰易懂

## 资源

### 文档

- [AGENT.md](../AGENT.md) - Agent 行为规约
- [system.spec.md](system.spec.md) - 系统规格
- [algorithms.spec.md](layers/algorithms.spec.md) - 算法层规格
- [api.spec.md](layers/api.spec.md) - API 层规格
- [core.spec.md](layers/core.spec.md) - 核心层规格
- [client.spec.md](layers/client.spec.md) - 客户端 SDK 层规格
- [001-core-system.md](001-core-system.md) - 核心系统规格
- [002-algorithms.md](002-algorithms.md) - 算法层详细规格
- [003-api-layer.md](003-api-layer.md) - API 层详细规格
- [004-client-sdks.md](004-client-sdks.md) - 客户端 SDK 详细规格
- [005-development-guide.md](005-development-guide.md) - 开发指南

### 工具

- [Markdown 编辑器](https://www.markdownguide.org/tools/)
- [Spec 模板](https://github.com/github/spec-template)

### 社区

- GitHub Issues: https://github.com/hsbreeze01/chunk-optimizer/issues
- Discussions: https://github.com/hsbreeze01/chunk-optimizer/discussions

## 版本历史

### v0.2.0 (2024-01-17)

- 添加 AGENT.md - Agent 行为规约
- 添加 spec/system.spec.md - 系统规格
- 添加 spec/layers/ 目录 - 层级规约
- 添加 algorithms.spec.md - 算法层规格
- 添加 api.spec.md - API 层规格
- 添加 core.spec.md - 核心层规格
- 添加 client.spec.md - 客户端 SDK 层规格
- 更新 README.md - 添加 base 规约说明

### v0.1.0 (2024-01-17)

- 初始版本
- 创建 5 个核心 spec 文档
- 建立 Spec-Driven 开发流程
- 定义开发规范和最佳实践
