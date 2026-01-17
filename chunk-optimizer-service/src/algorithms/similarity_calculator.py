"""Similarity calculator for chunks"""
import re
from typing import List, Set
from collections import Counter


class SimilarityCalculator:
    """Calculate similarity between chunks"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这'
        }
    
    def analyze(self, content: str) -> float:
        """Analyze similarity and return score (0-1)"""
        if not content or not content.strip():
            return 0.0
        
        words = self._extract_words(content)
        
        if len(words) < 5:
            return 0.0
        
        return self._calculate_internal_similarity(words)
    
    def _extract_words(self, content: str) -> List[str]:
        """Extract meaningful words from content"""
        words = re.findall(r'\b\w+\b', content.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 1]
    
    def _calculate_internal_similarity(self, words: List[str]) -> float:
        """Calculate internal similarity within content"""
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
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two chunks"""
        words1 = set(self._extract_words(content1))
        words2 = set(self._extract_words(content2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        jaccard_similarity = len(intersection) / len(union)
        
        return jaccard_similarity
