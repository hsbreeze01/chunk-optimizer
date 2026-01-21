"""Size analyzer for chunks"""
from typing import Optional
from config.domain_config import DomainConfig


class SizeAnalyzer:
    """Analyze chunk size"""
    
    def __init__(self, config: Optional[DomainConfig] = None):
        if config is None:
            config = DomainConfig()
        
        self.min_length = config.min_length
        self.max_length = config.max_length
        self.optimal_min = config.optimal_length[0]
        self.optimal_max = config.optimal_length[1]
    
    def analyze(self, content: str) -> float:
        """Analyze chunk size and return score (0-1)"""
        if not content or not content.strip():
            return 0.0
        
        length = len(content)
        
        if length < self.min_length:
            return length / self.min_length
        elif length > self.max_length:
            return max(0, 1 - (length - self.max_length) / self.max_length)
        elif self.optimal_min <= length <= self.optimal_max:
            return 1.0
        elif self.min_length <= length < self.optimal_min:
            return 0.6 + 0.4 * (length - self.min_length) / (self.optimal_min - self.min_length)
        else:
            return 0.6 + 0.4 * (self.max_length - length) / (self.max_length - self.optimal_max)
