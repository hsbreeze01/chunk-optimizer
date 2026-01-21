"""Redundancy detector for chunks"""
import re
from typing import List, Tuple, Optional
from collections import Counter


class RedundancyDetector:
    """Detect redundant content in chunks"""
    
    def __init__(self, config: Optional = None):
        self.min_phrase_length = 3
        self.max_phrase_length = 8
        self.repetition_threshold = 2
        
        # Pre-compile regex pattern for performance
        self.word_pattern = re.compile(r'\b\w+\b')
        self.sentence_pattern = re.compile(r'[.!?]+')
    
    def analyze(self, content: str) -> float:
        """Analyze redundancy and return score (0-1)"""
        if not content or not content.strip():
            return 0.0
        
        scores = []
        
        scores.append(self._detect_phrase_repetition(content))
        scores.append(self._detect_sentence_repetition(content))
        scores.append(self._detect_word_repetition(content))
        
        return sum(scores) / len(scores)
    
    def _detect_phrase_repetition(self, content: str) -> float:
        """Detect repeated phrases with optimized algorithm"""
        words = self.word_pattern.findall(content.lower())
        
        if len(words) < self.min_phrase_length * 2:
            return 0.0
        
        # Optimized: Use sliding window to avoid O(n^3) complexity
        phrase_counts = {}
        window_size = min(self.max_phrase_length, len(words))
        
        for i in range(len(words)):
            max_j = min(i + window_size + 1, len(words) + 1)
            for j in range(i + self.min_phrase_length, max_j):
                phrase = ' '.join(words[i:j])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Count repeated phrases
        repeated_phrases = [p for p, c in phrase_counts.items() if c >= self.repetition_threshold]
        
        if not repeated_phrases:
            return 0.0
        
        redundancy_score = sum(c - 1 for c in phrase_counts.values() if c >= self.repetition_threshold)
        max_possible = len(phrase_counts) * 0.5
        
        return min(1.0, redundancy_score / max_possible) if max_possible > 0 else 0.0
    
    def _detect_sentence_repetition(self, content: str) -> float:
        """Detect repeated sentences"""
        sentences = self.sentence_pattern.split(content)
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
    
    def _detect_word_repetition(self, content: str) -> float:
        """Detect excessive word repetition"""
        words = self.word_pattern.findall(content.lower())
        
        if not words:
            return 0.0
        
        word_counts = Counter(words)
        total_words = len(words)
        unique_words = len(word_counts)
        
        if total_words < 10:
            return 0.0
        
        diversity_ratio = unique_words / total_words
        
        if diversity_ratio >= 0.7:
            return 0.0
        elif diversity_ratio >= 0.5:
            return 0.3
        elif diversity_ratio >= 0.3:
            return 0.6
        else:
            return 1.0
