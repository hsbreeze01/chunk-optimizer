# Algorithms Layer Specification

## Responsibility

* 实现核心分析算法
* 提供质量评估、重复检测、大小分析、相似度计算功能
* 与技术实现无关，专注于算法逻辑

## Scope

`chunk-optimizer-service/src/algorithms/`

## Allowed Files

* `quality_analyzer.py` - 质量分析器
* `redundancy_detector.py` - 重复检测器
* `size_analyzer.py` - 大小分析器
* `similarity_calculator.py` - 相似度计算器

## Dependencies

* 仅允许 Python 标准库
* `re` - 正则表达式
* `collections` - Counter
* `typing` - 类型提示

## Forbidden

* 访问 infrastructure（数据库、缓存、LLM）
* 调用第三方 SDK
* IO 操作（文件读写、网络请求）
* 数据库访问

## Implementation Requirements

### QualityAnalyzer

* **Method**: `analyze(content: str) -> float`
* **Output**: 质量分数，范围 [0, 1]
* **Dimensions**:
  * 长度分析（权重 40%）
  * 句子结构分析（权重 20%）
  * 词汇多样性分析（权重 20%）
  * 连贯性分析（权重 20%）
* **Parameters**:
  * `min_length`: 50 字符
  * `max_length`: 2000 字符
  * `optimal_length`: (300, 1000) 字符
* **Performance**: < 50ms for 1000 chars

### RedundancyDetector

* **Method**: `analyze(content: str) -> float`
* **Output**: 冗余分数，范围 [0, 1]
* **Dimensions**:
  * 短语重复检测（权重 40%）
  * 句子重复检测（权重 30%）
  * 单词重复检测（权重 30%）
* **Parameters**:
  * `min_phrase_length`: 3 词
  * `max_phrase_length`: 8 词
  * `repetition_threshold`: 2 次
* **Performance**: < 100ms for 1000 chars

### SizeAnalyzer

* **Method**: `analyze(content: str) -> float`
* **Output**: 大小分数，范围 [0, 1]
* **Parameters**:
  * `min_length`: 50 字符
  * `max_length`: 2000 字符
  * `optimal_min`: 300 字符
  * `optimal_max`: 1000 字符
* **Performance**: < 1ms

### SimilarityCalculator

* **Method**: `calculate_similarity(content1: str, content2: str) -> float`
* **Output**: 相似度分数，范围 [0, 1]
* **Method**: Jaccard 相似度
* **Stop Words**: 预定义的中英文停用词列表
* **Performance**: < 50ms for 1000 chars

## Testing Requirements

* 所有算法必须有单元测试
* 测试覆盖率 >= 90%
* 必须测试所有边界条件
* 必须测试性能要求

## Notes

* 这是系统中最稳定的层
* 算法逻辑不应随时间频繁变化
* 所有算法实现必须参考 `spec/002-algorithms.md` 中的详细规格
