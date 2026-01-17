"""Redundancy detector for chunks"""
import re
from typing import List, Tuple
from collections import Counter


class RedundancyDetector:
    """Detect redundant content in chunks"""
    
    def __init__(self):
        self.min_phrase_length = 3
        self.max_phrase_length = 8
        self.repetition_threshold = 2
    
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
        """Detect repeated phrases"""
        words = re.findall(r'\b\w+\b', content.lower())
        
        if len(words) < self.min_phrase_length * 2:
            return 0.0
        
        phrases = []
        for length in range(self.min_phrase_length, min(self.max_phrase_length + 1, len(words))):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i + length])
                phrases.append(phrase)
        
        phrase_counts = Counter(phrases)
        repeated_phrases = [p for p, c in phrase_counts.items() if c >= self.repetition_threshold]
        
        if not repeated_phrases:
            return 0.0
        
        redundancy_score = sum(c - 1 for c in phrase_counts.values() if c >= self.repetition_threshold)
        max_possible = len(phrases) * 0.5
        
        return min(1.0, redundancy_score / max_possible)
    
    def _detect_sentence_repetition(self, content: str) -> float:
        """Detect repeated sentences"""
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
    
    def _detect_word_repetition(self, content: str) -> float:
        """Detect excessive word repetition"""
        words = re.findall(r'\b\w+\b', content.lower())
        
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
