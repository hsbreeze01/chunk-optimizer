"""Domain-specific configurations for chunk optimization"""
from pydantic import BaseModel
from typing import Tuple
from functools import lru_cache


class DomainConfig(BaseModel):
    """Domain-specific configuration"""
    
    # 权重配置
    quality_weight: float = 0.4
    redundancy_weight: float = 0.3
    size_weight: float = 0.2
    similarity_weight: float = 0.1
    
    # 阈值配置
    quality_threshold: float = 0.6
    redundancy_threshold: float = 0.5
    size_threshold: float = 0.5
    similarity_threshold: float = 0.85
    
    # 算法参数
    min_length: int = 50
    max_length: int = 2000
    optimal_length: Tuple[int, int] = (300, 1000)
    
    def get_weights(self) -> dict:
        """Get weight configuration"""
        return {
            "quality": self.quality_weight,
            "redundancy": self.redundancy_weight,
            "size": self.size_weight,
            "similarity": self.similarity_weight
        }
    
    def get_thresholds(self) -> dict:
        """Get threshold configuration"""
        return {
            "quality": self.quality_threshold,
            "redundancy": self.redundancy_threshold,
            "size": self.size_threshold,
            "similarity": self.similarity_threshold
        }
    
    def get_algorithm_params(self) -> dict:
        """Get algorithm parameters"""
        return {
            "min_length": self.min_length,
            "max_length": self.max_length,
            "optimal_length": self.optimal_length
        }
    
    def __hash__(self):
        """Make DomainConfig hashable for caching"""
        return hash((
            self.quality_weight,
            self.redundancy_weight,
            self.size_weight,
            self.similarity_weight,
            self.quality_threshold,
            self.redundancy_threshold,
            self.size_threshold,
            self.similarity_threshold,
            self.min_length,
            self.max_length,
            self.optimal_length
        ))


@lru_cache(maxsize=10)
def get_domain_config(domain: str) -> DomainConfig:
    """Get domain-specific configuration with caching"""
    domain = domain.lower()
    
    if domain == "operations":
        return DomainConfig(
            # 运维领域：更重视质量和冗余
            quality_weight=0.5,           # 提高质量权重
            redundancy_weight=0.3,        # 保持冗余权重
            size_weight=0.15,             # 降低大小权重
            similarity_weight=0.05,       # 降低相似度权重
            
            # 更严格的阈值
            quality_threshold=0.7,        # 提高质量阈值
            redundancy_threshold=0.4,    # 降低冗余阈值（更严格）
            size_threshold=0.4,           # 降低大小阈值
            similarity_threshold=0.9,     # 提高相似度阈值
            
            # 更长的内容长度
            min_length=100,               # 提高最小长度
            max_length=3000,             # 提高最大长度
            optimal_length=(500, 1500)    # 调整最优长度范围
        )
    elif domain == "ecommerce":
        return DomainConfig(
            # 电商领域：平衡各项指标，更重视大小和相似度
            quality_weight=0.3,           # 降低质量权重
            redundancy_weight=0.25,       # 降低冗余权重
            size_weight=0.25,             # 提高大小权重
            similarity_weight=0.2,        # 提高相似度权重
            
            # 标准阈值
            quality_threshold=0.6,        # 保持默认质量阈值
            redundancy_threshold=0.5,     # 保持默认冗余阈值
            size_threshold=0.6,           # 提高大小阈值
            similarity_threshold=0.8,     # 降低相似度阈值（更严格）
            
            # 更短的内容长度
            min_length=50,                # 保持最小长度
            max_length=1500,             # 降低最大长度
            optimal_length=(200, 800)     # 调整最优长度范围
        )
    elif domain == "medical":
        return DomainConfig(
            # 医疗领域：极其重视质量和冗余
            quality_weight=0.6,           # 大幅提高质量权重
            redundancy_weight=0.25,       # 提高冗余权重
            size_weight=0.1,              # 大大降低大小权重
            similarity_weight=0.05,       # 大大降低相似度权重
            
            # 非常严格的阈值
            quality_threshold=0.8,        # 大幅提高质量阈值
            redundancy_threshold=0.3,     # 大幅降低冗余阈值（非常严格）
            size_threshold=0.5,           # 保持大小阈值
            similarity_threshold=0.95,    # 大幅提高相似度阈值（非常严格）
            
            # 更长的内容长度
            min_length=150,               # 提高最小长度
            max_length=5000,             # 提高最大长度
            optimal_length=(800, 2500)    # 调整最优长度范围
        )
    else:
        # 默认配置
        return DomainConfig()


def calculate_overall_score(
    quality_score: float,
    redundancy_score: float,
    size_score: float,
    similarity_score: float,
    config: DomainConfig = None
) -> float:
    """Calculate overall score using domain-specific weights"""
    if config is None:
        config = DomainConfig()
    
    return (
        quality_score * config.quality_weight +
        (1 - redundancy_score) * config.redundancy_weight +
        size_score * config.size_weight +
        (1 - similarity_score) * config.similarity_weight
    )


def get_optimization_priority(
    score: float,
    threshold: float,
    high_threshold: float = None
) -> str:
    """Get optimization priority based on score and threshold"""
    if high_threshold is None:
        high_threshold = threshold * 0.8  # 默认高优先级阈值为阈值的80%
    
    if score < high_threshold:
        return "HIGH"
    elif score < threshold:
        return "MEDIUM"
    else:
        return "LOW"
