# Chunk Optimizer 算法层规格

## 概述

本文档详细描述 Chunk Optimizer 中所有算法的实现细节、输入输出、边界条件和性能要求。

## 算法架构

```
Algorithms/
├── QualityAnalyzer (质量分析器)
├── RedundancyDetector (重复检测器)
├── SizeAnalyzer (大小分析器)
└── SimilarityCalculator (相似度计算器)
```

---

## 1. QualityAnalyzer（质量分析器）

### 1.1 目标

从多个维度评估 Chunk 的内容质量，为优化建议提供依据。

### 1.2 输入

```python
content: str  # Chunk 文本内容
```

### 1.3 输出

```python
score: float  # 质量分数，范围 [0, 1]
```

### 1.4 评分维度

#### 1.4.1 长度分析 (_analyze_length)

**权重**: 40%

**参数**:
- `min_length`: 50 字符
- `max_length`: 2000 字符
- `optimal_length`: (300, 1000) 字符

**评分函数**:
```python
def _analyze_length(content: str) -> float:
    length = len(content)
    
    if length < min_length:
        # 线性增长：从 0 到 1
        return length / min_length
    elif length > max_length:
        # 线性衰减：从 1 到 0
        return max(0, 1 - (length - max_length) / max_length)
    elif optimal_length[0] <= length <= optimal_length[1]:
        # 最优区间：满分
        return 1.0
    else:
        # 次优区间：0.8 分
        return 0.8
```

**边界条件**:
- 空字符串: 返回 0.0
- 长度 < 50: 返回 length / 50
- 长度 > 2000: 返回 max(0, 1 - (length - 2000) / 2000)
- 长度 = 2000: 返回 0.0

**测试用例**:
| 长度 | 预期分数 | 说明 |
|------|---------|------|
| 0 | 0.0 | 空字符串 |
| 25 | 0.5 | 最小值的一半 |
| 50 | 1.0 | 最小值 |
| 300 | 1.0 | 最优区间下限 |
| 500 | 1.0 | 最优区间中间 |
| 1000 | 1.0 | 最优区间上限 |
| 1500 | 0.8 | 次优区间 |
| 2000 | 0.0 | 最大值 |
| 2500 | 0.0 | 超过最大值 |

#### 1.4.2 句子结构分析 (_analyze_sentence_structure)

**权重**: 20%

**参数**:
- 最优句子长度: 10-25 词

**评分函数**:
```python
def _analyze_sentence_structure(content: str) -> float:
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
    
    if 10 <= avg_sentence_length <= 25:
        return 1.0
    elif 5 <= avg_sentence_length < 10 or 25 < avg_sentence_length <= 35:
        return 0.7
    else:
        return 0.5
```

**边界条件**:
- 空字符串: 返回 0.0
- 单句: 正常计算
- 句子长度 < 5 词: 返回 0.5
- 句子长度 > 35 词: 返回 0.5

**测试用例**:
| 平均句长 | 预期分数 | 说明 |
|---------|---------|------|
| 3 | 0.5 | 过短 |
| 7 | 0.7 | 偏短 |
| 15 | 1.0 | 最优 |
| 30 | 0.7 | 偏长 |
| 40 | 0.5 | 过长 |

#### 1.4.3 词汇多样性分析 (_analyze_vocabulary)

**权重**: 20%

**参数**:
- 最优多样性: >= 60%

**评分函数**:
```python
def _analyze_vocabulary(content: str) -> float:
    words = re.findall(r'\b\w+\b', content.lower())
    
    if not words:
        return 0.0
    
    unique_words = set(words)
    diversity = len(unique_words) / len(words)
    
    if diversity >= 0.6:
        return 1.0
    elif diversity >= 0.4:
        return 0.8
    else:
        return 0.5
```

**边界条件**:
- 空字符串: 返回 0.0
- 无单词: 返回 0.0
- 所有单词相同: 返回 0.5

**测试用例**:
| 多样性 | 预期分数 | 说明 |
|-------|---------|------|
| 0.2 | 0.5 | 低多样性 |
| 0.5 | 0.8 | 中等多样性 |
| 0.7 | 1.0 | 高多样性 |
| 1.0 | 1.0 | 完全多样性 |

#### 1.4.4 连贯性分析 (_analyze_coherence)

**权重**: 20%

**参数**:
- 基础分: 0.8
- 连接词奖励: +0.2

**连接词列表**:
```python
transition_words = [
    # 英文
    'however', 'therefore', 'consequently', 'furthermore',
    'moreover', 'in addition', 'meanwhile', 'otherwise',
    'thus', 'hence', 'accordingly', 'nevertheless',
    # 中文
    '但是', '因此', '所以', '此外', '而且', '同时', '否则',
    '于是', '从而', '然而', '不过'
]
```

**评分函数**:
```python
def _analyze_coherence(content: str) -> float:
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.8
    
    coherence_score = 0.8
    
    has_transitions = any(
        any(word in sentence.lower() for word in transition_words)
        for sentence in sentences
    )
    
    if has_transitions:
        coherence_score += 0.2
    
    return min(1.0, coherence_score)
```

**边界条件**:
- 空字符串: 返回 0.0
- 单句: 返回 0.8
- 多句无连接词: 返回 0.8
- 多句有连接词: 返回 1.0

**测试用例**:
| 句子数 | 连接词 | 预期分数 | 说明 |
|-------|-------|---------|------|
| 0 | - | 0.0 | 空字符串 |
| 1 | - | 0.8 | 单句 |
| 2 | 无 | 0.8 | 多句无连接词 |
| 2 | 有 | 1.0 | 多句有连接词 |

### 1.5 综合评分

```python
def analyze(content: str) -> float:
    if not content or not content.strip():
        return 0.0
    
    scores = []
    scores.append(_analyze_length(content))      # 40%
    scores.append(_analyze_sentence_structure(content))  # 20%
    scores.append(_analyze_vocabulary(content))   # 20%
    scores.append(_analyze_coherence(content))    # 20%
    
    return sum(scores) / len(scores)
```

### 1.6 性能要求

- 时间复杂度: O(n)，n 为内容长度
- 空间复杂度: O(n)，存储句子和单词
- 响应时间: < 50ms for 1000 chars

---

## 2. RedundancyDetector（重复检测器）

### 2.1 目标

检测 Chunk 内部的重复内容，包括短语、句子和单词重复。

### 2.2 输入

```python
content: str  # Chunk 文本内容
```

### 2.3 输出

```python
score: float  # 冗余分数，范围 [0, 1]
```

### 2.4 检测维度

#### 2.4.1 短语重复检测 (_detect_phrase_repetition)

**权重**: 40%

**参数**:
- `min_phrase_length`: 3 词
- `max_phrase_length`: 8 词
- `repetition_threshold`: 2 次

**检测逻辑**:
```python
def _detect_phrase_repetition(content: str) -> float:
    words = re.findall(r'\b\w+\b', content.lower())
    
    if len(words) < min_phrase_length * 2:
        return 0.0
    
    phrases = []
    for length in range(min_phrase_length, min(max_phrase_length + 1, len(words))):
        for i in range(len(words) - length + 1):
            phrase = ' '.join(words[i:i + length])
            phrases.append(phrase)
    
    phrase_counts = Counter(phrases)
    repeated_phrases = [p for p, c in phrase_counts.items() if c >= repetition_threshold]
    
    if not repeated_phrases:
        return 0.0
    
    redundancy_score = sum(c - 1 for c in phrase_counts.values() if c >= repetition_threshold)
    max_possible = len(phrases) * 0.5
    
    return min(1.0, redundancy_score / max_possible)
```

**边界条件**:
- 空字符串: 返回 0.0
- 词数 < 6: 返回 0.0
- 无重复短语: 返回 0.0

**测试用例**:
| 内容 | 预期分数 | 说明 |
|------|---------|------|
| "hello world" | 0.0 | 词数不足 |
| "hello world hello world" | 0.5 | 2词短语重复2次 |
| "hello world test hello world test" | 0.33 | 3词短语重复2次 |

#### 2.4.2 句子重复检测 (_detect_sentence_repetition)

**权重**: 30%

**参数**:
- 重复阈值: 2 次

**检测逻辑**:
```python
def _detect_sentence_repetition(content: str) -> float:
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip().lower() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.0
    
    sentence_counts = Counter(sentences)
    repeated_sentences = [s for s, c in sentence_counts.items() if c >= 2]
    
    if not repeated_sentences:
        return 0.0
    
    redundancy_score = sum(c - 1 for c in sentence_counts.values() if c >= 2)
    max_possible = len(sentences) * 0.5
    
    return min(1.0, redundancy_score / max_possible)
```

**边界条件**:
- 空字符串: 返回 0.0
- 单句: 返回 0.0
- 无重复句子: 返回 0.0

**测试用例**:
| 内容 | 预期分数 | 说明 |
|------|---------|------|
| "Hello world." | 0.0 | 单句 |
| "Hello world. Hello world." | 0.5 | 重复2次 |
| "Hello world. Hello world. Hello world." | 1.0 | 重复3次 |

#### 2.4.3 单词重复检测 (_detect_word_repetition)

**权重**: 30%

**参数**:
- 最小词数: 10 词

**评分函数**:
```python
def _detect_word_repetition(content: str) -> float:
    words = re.findall(r'\b\w+\b', content.lower())
    
    if not words:
        return 0.0
    
    if len(words) < 10:
        return 0.0
    
    word_counts = Counter(words)
    total_words = len(words)
    unique_words = len(word_counts)
    
    diversity_ratio = unique_words / total_words
    
    if diversity_ratio >= 0.7:
        return 0.0
    elif diversity_ratio >= 0.5:
        return 0.3
    elif diversity_ratio >= 0.3:
        return 0.6
    else:
        return 1.0
```

**边界条件**:
- 空字符串: 返回 0.0
- 词数 < 10: 返回 0.0
- 所有单词相同: 返回 1.0

**测试用例**:
| 多样性 | 预期分数 | 说明 |
|-------|---------|------|
| 0.2 | 1.0 | 高重复 |
| 0.4 | 0.6 | 中度重复 |
| 0.6 | 0.3 | 轻度重复 |
| 0.8 | 0.0 | 无重复 |

### 2.5 综合评分

```python
def analyze(content: str) -> float:
    if not content or not content.strip():
        return 0.0
    
    scores = []
    scores.append(_detect_phrase_repetition(content))    # 40%
    scores.append(_detect_sentence_repetition(content))  # 30%
    scores.append(_detect_word_repetition(content))      # 30%
    
    return sum(scores) / len(scores)
```

### 2.6 性能要求

- 时间复杂度: O(n²)，n 为单词数量（短语检测）
- 空间复杂度: O(n²)，存储所有短语
- 响应时间: < 100ms for 1000 chars

---

## 3. SizeAnalyzer（大小分析器）

### 3.1 目标

评估 Chunk 长度是否在合理范围内，提供分段建议。

### 3.2 输入

```python
content: str  # Chunk 文本内容
```

### 3.3 输出

```python
score: float  # 大小分数，范围 [0, 1]
```

### 3.4 评分函数

**参数**:
- `min_length`: 50 字符
- `max_length`: 2000 字符
- `optimal_min`: 300 字符
- `optimal_max`: 1000 字符

```python
def analyze(content: str) -> float:
    if not content or not content.strip():
        return 0.0
    
    length = len(content)
    
    if length < min_length:
        # 线性增长：从 0 到 1
        return length / min_length
    elif length > max_length:
        # 线性衰减：从 1 到 0
        return max(0, 1 - (length - max_length) / max_length)
    elif optimal_min <= length <= optimal_max:
        # 最优区间：满分
        return 1.0
    elif min_length <= length < optimal_min:
        # 次优区间（偏短）：线性插值
        return 0.6 + 0.4 * (length - min_length) / (optimal_min - min_length)
    else:
        # 次优区间（偏长）：线性插值
        return 0.6 + 0.4 * (max_length - length) / (max_length - optimal_max)
```

### 3.5 边界条件

- 空字符串: 返回 0.0
- 长度 = 50: 返回 1.0
- 长度 = 300: 返回 1.0
- 长度 = 1000: 返回 1.0
- 长度 = 2000: 返回 0.0

### 3.6 测试用例

| 长度 | 预期分数 | 说明 |
|------|---------|------|
| 0 | 0.0 | 空字符串 |
| 25 | 0.5 | 最小值的一半 |
| 50 | 1.0 | 最小值 |
| 175 | 0.8 | 次优区间中间 |
| 300 | 1.0 | 最优区间下限 |
| 650 | 1.0 | 最优区间中间 |
| 1000 | 1.0 | 最优区间上限 |
| 1500 | 0.8 | 次优区间中间 |
| 2000 | 0.0 | 最大值 |
| 2500 | 0.0 | 超过最大值 |

### 3.7 性能要求

- 时间复杂度: O(1)，常数时间
- 空间复杂度: O(1)，常数空间
- 响应时间: < 1ms

---

## 4. SimilarityCalculator（相似度计算器）

### 4.1 目标

计算 Chunk 内部的相似度（内部重复）和两个 Chunk 之间的相似度（跨 Chunk 重复）。

### 4.2 输入

```python
content: str  # Chunk 文本内容
other_content: str (可选)  # 另一个 Chunk 的内容
```

### 4.3 输出

```python
score: float  # 相似度分数，范围 [0, 1]
```

### 4.4 停用词列表

```python
stop_words = {
    # 英文
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    # 中文
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
    '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
    '看', '好', '自己', '这'
}
```

### 4.5 内部相似度计算 (_calculate_internal_similarity)

**参数**:
- 最小词数: 5 词
- 最大重复比例: 0.3

```python
def _calculate_internal_similarity(content: str) -> float:
    words = _extract_words(content)
    
    if len(words) < 5:
        return 0.0
    
    word_counts = Counter(words)
    repeated_words = {w: c for w, c in word_counts.items() if c >= 2}
    
    if not repeated_words:
        return 0.0
    
    total_repetitions = sum(c - 1 for c in repeated_words.values())
    max_possible = len(words) * 0.3
    
    similarity_score = total_repetitions / max_possible if max_possible > 0 else 0.0
    
    return min(1.0, similarity_score)
```

### 4.6 Jaccard 相似度计算 (calculate_similarity)

**公式**:
```python
J(A, B) = |A ∩ B| / |A ∪ B|
```

```python
def calculate_similarity(content1: str, content2: str) -> float:
    words1 = set(_extract_words(content1))
    words2 = set(_extract_words(content2))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    if not union:
        return 0.0
    
    jaccard_similarity = len(intersection) / len(union)
    
    return jaccard_similarity
```

### 4.7 边界条件

- 空字符串: 返回 0.0
- 词数 < 5: 返回 0.0
- 无重复词: 返回 0.0
- 完全相同: 返回 1.0

### 4.8 测试用例

**内部相似度**:
| 内容 | 预期分数 | 说明 |
|------|---------|------|
| "hello" | 0.0 | 词数不足 |
| "hello world hello" | 0.33 | 重复1次 |
| "hello world hello world" | 0.5 | 重复2次 |

**Jaccard 相似度**:
| 内容1 | 内容2 | 预期分数 | 说明 |
|-------|-------|---------|------|
| "hello world" | "hello world" | 1.0 | 完全相同 |
| "hello world" | "hello test" | 0.5 | 部分相同 |
| "hello world" | "test foo" | 0.0 | 完全不同 |

### 4.9 性能要求

- 时间复杂度: O(n)，n 为单词数量
- 空间复杂度: O(n)，存储单词计数
- 响应时间: < 50ms for 1000 chars

---

## 5. 算法集成

### 5.1 Optimizer（优化引擎）

**目标**: 整合所有算法，生成综合优化建议。

**输入**:
```python
chunk_id: str
content: str
options: AnalysisOptions
```

**输出**:
```python
OptimizationResponse {
    optimization: Optimization
    metrics: Metrics
}
```

### 5.2 综合评分权重

```python
overall_score = (
    quality_score * 0.4 +          # 40% 权重
    (1 - redundancy_score) * 0.3 + # 30% 权重
    size_score * 0.2 +              # 20% 权重
    (1 - similarity_score) * 0.1    # 10% 权重
)
```

### 5.3 优化建议生成规则

#### 5.3.1 质量优化

**触发条件**: `quality_score < 0.6`

**优先级**:
- `quality_score < 0.4`: HIGH
- `0.4 <= quality_score < 0.6`: MEDIUM

**建议内容**:
- 标题: "Chunk quality needs improvement"
- 描述: "Quality score is {score:.2f}, which is below the recommended threshold of 0.6"
- 行动: "Review and rewrite the chunk to improve clarity, coherence, and completeness"

#### 5.3.2 冗余优化

**触发条件**: `redundancy_score > 0.5`

**优先级**:
- `redundancy_score > 0.7`: HIGH
- `0.5 < redundancy_score <= 0.7`: MEDIUM

**建议内容**:
- 标题: "Redundant content detected"
- 描述: "Redundancy score is {score:.2f}, indicating significant repetitive content"
- 行动: "Remove or consolidate redundant information to improve efficiency"

#### 5.3.3 大小优化

**触发条件**: `size_score < 0.5`

**优先级**: MEDIUM

**建议内容**:
- 标题: "Chunk size is suboptimal"
- 描述: "Size score is {score:.2f}, indicating the chunk may be too short or too long"
- 行动: "Adjust chunk size to optimal range (300-1000 characters)"

#### 5.3.4 相似度优化

**触发条件**: `similarity_score > 0.85`

**优先级**: HIGH

**建议内容**:
- 标题: "Highly similar content detected"
- 描述: "Similarity score is {score:.2f}, indicating potential duplicate content"
- 行动: "Review and merge with similar chunks to avoid redundancy"

---

## 6. 性能优化建议

### 6.1 短语重复检测优化

**当前问题**: O(n²) 时间复杂度

**优化方案**: 使用滑动窗口

```python
def _detect_phrase_repetition_optimized(content: str) -> float:
    words = re.findall(r'\b\w+\b', content.lower())
    
    if len(words) < self.min_phrase_length * 2:
        return 0.0
    
    phrase_counts = Counter()
    
    for length in range(self.min_phrase_length, self.max_phrase_length + 1):
        if length > len(words):
            break
        
        window = ' '.join(words[:length])
        phrase_counts[window] += 1
        
        for i in range(length, len(words)):
            window = ' '.join(words[i - length + 1:i + 1])
            phrase_counts[window] += 1
    
    repeated_phrases = {p: c for p, c in phrase_counts.items() if c >= self.repetition_threshold}
    
    if not repeated_phrases:
        return 0.0
    
    redundancy_score = sum(c - 1 for c in repeated_phrases.values())
    max_possible = sum(phrase_counts.values()) * 0.5
    
    return min(1.0, redundancy_score / max_possible) if max_possible > 0 else 0.0
```

### 6.2 缓存优化

**场景**: 相同内容多次分析

**方案**: 使用 LRU 缓存

```python
from functools import lru_cache

class QualityAnalyzer:
    @lru_cache(maxsize=1000)
    def analyze(self, content: str) -> float:
        # ... 原有逻辑
        pass
```

### 6.3 并行处理

**场景**: 批量分析多个 Chunks

**方案**: 使用 asyncio 或多线程

```python
async def analyze_batch(self, items: List[BatchItem]) -> List[OptimizationResponse]:
    tasks = [self.analyze_chunk(item.chunk_id, item.content) for item in items]
    return await asyncio.gather(*tasks)
```

---

## 7. 测试要求

### 7.1 单元测试

每个算法需要覆盖以下测试场景：
- 正常输入
- 边界条件
- 异常输入
- 性能测试

### 7.2 集成测试

测试算法之间的协作：
- Optimizer 整合所有算法
- 批量分析功能
- 文档分析功能

### 7.3 性能测试

- 响应时间测试
- 并发测试
- 压力测试

---

## 8. 未来改进方向

### 8.1 短期改进

1. 优化短语检测性能（O(n²) -> O(n)）
2. 添加自适应阈值
3. 改进连贯性分析

### 8.2 中期改进

1. 集成词向量模型
2. 添加语义相似度检测
3. 支持多语言

### 8.3 长期改进

1. 训练机器学习模型
2. 实现深度学习质量预测
3. 添加用户反馈学习
