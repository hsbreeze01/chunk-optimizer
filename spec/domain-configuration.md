# 领域配置指南

## 概述

chunk-optimizer 支持针对不同业务领域（运维、电商、医疗等）进行配置化，通过调整权重、阈值和算法参数，实现领域特定的优化策略。

---

## 预定义领域

### 1. 运维领域 (operations)

**业务特点**：
- 配置文档需要准确、完整
- 避免重复配置导致冲突
- 文档需要清晰、结构化

**配置参数**：

```python
{
    "quality_weight": 0.5,           # 提高质量权重
    "redundancy_weight": 0.3,        # 保持冗余权重
    "size_weight": 0.15,             # 降低大小权重
    "similarity_weight": 0.05,       # 降低相似度权重
    
    "quality_threshold": 0.7,        # 提高质量阈值
    "redundancy_threshold": 0.4,    # 降低冗余阈值（更严格）
    "size_threshold": 0.4,           # 降低大小阈值
    "similarity_threshold": 0.9,     # 提高相似度阈值
    
    "min_length": 100,               # 提高最小长度
    "max_length": 3000,             # 提高最大长度
    "optimal_length": (500, 1500)    # 调整最优长度范围
}
```

**适用场景**：
- 系统配置文档分析
- 运维手册优化
- 技术文档质量评估

---

### 2. 电商领域 (ecommerce)

**业务特点**：
- 商品描述需要简洁、吸引人
- 避免重复商品描述
- 关注 SEO 和用户体验

**配置参数**：

```python
{
    "quality_weight": 0.3,           # 降低质量权重
    "redundancy_weight": 0.25,       # 降低冗余权重
    "size_weight": 0.25,             # 提高大小权重
    "similarity_weight": 0.2,        # 提高相似度权重
    
    "quality_threshold": 0.6,        # 保持默认质量阈值
    "redundancy_threshold": 0.5,     # 保持默认冗余阈值
    "size_threshold": 0.6,           # 提高大小阈值
    "similarity_threshold": 0.8,     # 降低相似度阈值（更严格）
    
    "min_length": 50,                # 保持最小长度
    "max_length": 1500,             # 降低最大长度
    "optimal_length": (200, 800)     # 调整最优长度范围
}
```

**适用场景**：
- 商品描述优化
- 产品文档分析
- 营销内容质量评估

---

### 3. 医疗领域 (medical)

**业务特点**：
- 医疗记录必须准确、完整
- 避免重复记录导致误诊
- 关注专业术语和结构化

**配置参数**：

```python
{
    "quality_weight": 0.6,           # 大幅提高质量权重
    "redundancy_weight": 0.25,       # 提高冗余权重
    "size_weight": 0.1,              # 大大降低大小权重
    "similarity_weight": 0.05,       # 大大降低相似度权重
    
    "quality_threshold": 0.8,        # 大幅提高质量阈值
    "redundancy_threshold": 0.3,     # 大幅降低冗余阈值（非常严格）
    "size_threshold": 0.5,           # 保持大小阈值
    "similarity_threshold": 0.95,    # 大幅提高相似度阈值（非常严格）
    
    "min_length": 150,               # 提高最小长度
    "max_length": 5000,             # 提高最大长度
    "optimal_length": (800, 2500)    # 调整最优长度范围
}
```

**适用场景**：
- 医疗记录分析
- 诊断报告优化
- 医学文献质量评估

---

## 配置参数说明

### 权重配置

| 参数 | 说明 | 范围 | 默认值 |
|------|------|------|--------|
| `quality_weight` | 质量分数权重 | [0, 1] | 0.4 |
| `redundancy_weight` | 冗余分数权重 | [0, 1] | 0.3 |
| `size_weight` | 大小分数权重 | [0, 1] | 0.2 |
| `similarity_weight` | 相似度分数权重 | [0, 1] | 0.1 |

**注意事项**：
- 权重之和应该等于 1.0
- 权重越高，该维度对综合评分的影响越大

---

### 阈值配置

| 参数 | 说明 | 范围 | 默认值 |
|------|------|------|--------|
| `quality_threshold` | 质量分数阈值 | [0, 1] | 0.6 |
| `redundancy_threshold` | 冗余分数阈值 | [0, 1] | 0.5 |
| `size_threshold` | 大小分数阈值 | [0, 1] | 0.5 |
| `similarity_threshold` | 相似度分数阈值 | [0, 1] | 0.85 |

**注意事项**：
- 阈值用于判断是否需要优化
- 质量分数低于阈值 → 需要质量优化
- 冗余分数高于阈值 → 需要冗余优化
- 大小分数低于阈值 → 需要大小优化
- 相似度分数高于阈值 → 需要相似度优化

---

### 算法参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `min_length` | 最小长度（字符） | 50 |
| `max_length` | 最大长度（字符） | 2000 |
| `optimal_length` | 最优长度范围（字符） | (300, 1000) |

**注意事项**：
- 长度参数影响大小分数的计算
- 最优长度范围用于判断内容长度是否合适

---

## 使用方法

### 1. 获取领域配置

```python
from chunk_optimizer_service.src.config.domain_config import get_domain_config

# 获取运维领域配置
config = get_domain_config("operations")

# 获取电商领域配置
config = get_domain_config("ecommerce")

# 获取医疗领域配置
config = get_domain_config("medical")

# 获取默认配置
config = get_domain_config("default")
```

### 2. 计算综合评分

```python
from chunk_optimizer_service.src.config.domain_config import (
    get_domain_config,
    calculate_overall_score
)

# 获取领域配置
config = get_domain_config("medical")

# 计算综合评分
overall_score = calculate_overall_score(
    quality_score=0.75,
    redundancy_score=0.25,
    size_score=0.85,
    similarity_score=0.08,
    config=config
)

print(f"综合评分: {overall_score:.2f}")
```

### 3. 判断优化优先级

```python
from chunk_optimizer_service.src.config.domain_config import (
    get_domain_config,
    get_optimization_priority
)

# 获取领域配置
config = get_domain_config("medical")

# 判断优化优先级
priority = get_optimization_priority(
    score=0.75,
    threshold=config.quality_threshold
)

print(f"优化优先级: {priority}")  # 输出: HIGH, MEDIUM, 或 LOW
```

### 4. 在 API 中使用

```python
from fastapi import FastAPI, HTTPException
from chunk_optimizer_service.src.config.domain_config import get_domain_config

app = FastAPI()

@app.post("/api/v1/chunks/analyze")
async def analyze_chunk(
    chunk_id: str,
    content: str,
    domain: str = "default"
):
    # 获取领域配置
    config = get_domain_config(domain)
    
    # 使用配置进行分析
    # ...
    
    return {"result": "..."}
```

---

## 自定义领域配置

如果预定义的领域配置不满足需求，可以创建自定义配置：

```python
from chunk_optimizer_service.src.config.domain_config import DomainConfig

# 创建自定义配置
custom_config = DomainConfig(
    quality_weight=0.45,
    redundancy_weight=0.35,
    size_weight=0.15,
    similarity_weight=0.05,
    
    quality_threshold=0.65,
    redundancy_threshold=0.45,
    size_threshold=0.55,
    similarity_threshold=0.88,
    
    min_length=80,
    max_length=2500,
    optimal_length=(400, 1200)
)

# 使用自定义配置
from chunk_optimizer_service.src.config.domain_config import calculate_overall_score

overall_score = calculate_overall_score(
    quality_score=0.7,
    redundancy_score=0.3,
    size_score=0.8,
    similarity_score=0.1,
    config=custom_config
)
```

---

## 配置对比

### 相同分析结果在不同领域的综合评分

假设分析结果：
- 质量分数: 0.65
- 冗余分数: 0.35
- 大小分数: 0.75
- 相似度分数: 0.12

不同领域的综合评分：

| 领域 | 综合评分 | 说明 |
|------|----------|------|
| default | 0.62 | 默认配置 |
| operations | 0.64 | 运维领域（更重视质量） |
| ecommerce | 0.59 | 电商领域（更重视大小和相似度） |
| medical | 0.68 | 医疗领域（极其重视质量） |

---

## 最佳实践

### 1. 选择合适的领域

根据业务场景选择合适的领域配置：
- 运维文档 → `operations`
- 商品描述 → `ecommerce`
- 医疗记录 → `medical`
- 通用场景 → `default`

### 2. 调整配置参数

如果预定义配置不满足需求，可以调整参数：
- 提高某个维度的权重 → 该维度对综合评分影响更大
- 降低某个维度的阈值 → 更容易触发该维度的优化
- 调整长度参数 → 适应不同领域的内容长度需求

### 3. 测试和验证

在使用新配置前，建议进行测试和验证：
- 使用测试数据计算综合评分
- 检查优化建议是否符合预期
- 根据实际效果调整配置

### 4. 监控和优化

持续监控配置效果：
- 记录优化建议的接受率
- 收集用户反馈
- 根据反馈调整配置参数

---

## 示例代码

完整的使用示例请参考：
- [examples/domain_usage_example.py](../examples/domain_usage_example.py)

运行示例：

```bash
cd /Users/lancer.zhang/ProjectNIO/chunk-optimizer
python examples/domain_usage_example.py
```

---

## 常见问题

### Q: 如何添加新的领域配置？

A: 在 `chunk_optimizer_service/src/config/domain_config.py` 的 `get_domain_config` 函数中添加新的领域配置。

### Q: 权重之和必须等于 1.0 吗？

A: 是的，权重之和应该等于 1.0，以确保综合评分在 [0, 1] 范围内。

### Q: 如何判断配置是否合适？

A: 可以通过以下方式判断：
- 综合评分是否符合预期
- 优化建议是否合理
- 用户反馈是否积极

### Q: 可以在运行时动态切换领域配置吗？

A: 可以，每次调用分析接口时指定 `domain` 参数即可。

---

## 总结

chunk-optimizer 的领域配置功能使得系统能够适应不同业务场景的需求。通过合理配置权重、阈值和算法参数，可以实现领域特定的优化策略，提高优化建议的准确性和实用性。

选择合适的领域配置，根据实际需求调整参数，持续监控和优化，是使用领域配置功能的关键。
