# Core Layer Specification

## Responsibility

* 编排算法，生成优化建议
* 整合所有分析结果
* 计算综合评分
* 生成优化建议

## Scope

`chunk-optimizer-service/src/core/`

## Allowed Files

* `optimizer.py` - 优化引擎

## Dependencies

* `algorithms` - 所有算法实现
* `models` - 数据模型

## Forbidden

* 直接访问数据库
* 直接调用第三方 API
* 包含算法实现逻辑（算法逻辑在 algorithms 层）

## Implementation Requirements

### Optimizer

* **Methods**:
  * `analyze_chunk(chunk_id: str, content: str, metadata: dict) -> OptimizationResponse`
  * `analyze_document(document_id: str, chunks: List[Chunk], options: AnalysisOptions) -> DocumentAnalysisResponse`
  * `analyze_batch(items: List[Chunk], options: AnalysisOptions) -> BatchAnalysisResponse`
  * `calculate_similarity(content1: str, content2: str) -> float`

### Scoring Weights

综合评分权重（参考 `spec/002-algorithms.md`）：

```python
overall_score = (
    quality_score * 0.4 +          # 40% 权重
    (1 - redundancy_score) * 0.3 + # 30% 权重
    size_score * 0.2 +              # 20% 权重
    (1 - similarity_score) * 0.1    # 10% 权重
)
```

### Optimization Generation

优化建议生成规则（参考 `spec/002-algorithms.md`）：

1. **质量优化**:
   * 触发条件: `quality_score < 0.6`
   * 优先级: `quality_score < 0.4` → HIGH, `0.4 <= quality_score < 0.6` → MEDIUM

2. **冗余优化**:
   * 触发条件: `redundancy_score > 0.5`
   * 优先级: `redundancy_score > 0.7` → HIGH, `0.5 < redundancy_score <= 0.7` → MEDIUM

3. **大小优化**:
   * 触发条件: `size_score < 0.5`
   * 优先级: MEDIUM

4. **相似度优化**:
   * 触发条件: `similarity_score > 0.85`
   * 优先级: HIGH

## Testing Requirements

* 所有方法必须有单元测试
* 测试覆盖率 >= 90%
* 必须测试所有评分权重
* 必须测试所有优化建议生成规则
* 必须测试边界条件

## Notes

* Core 层负责"做什么"，不负责"怎么做"
* 算法实现逻辑在 algorithms 层
* Core 层只负责编排和整合
