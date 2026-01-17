"""Quality analyzer for chunks"""
import re
from typing import List


class QualityAnalyzer:
    """Analyze chunk quality"""
    
    def __init__(self):
        self.min_length = 50
        self.max_length = 2000
        self.optimal_length = (300, 1000)
    
    def analyze(self, content: str) -> float:
        """Analyze chunk quality and return score (0-1)"""
        if not content or not content.strip():
            return 0.0
        
        scores = []
        
        scores.append(self._analyze_length(content))
        scores.append(self._analyze_sentence_structure(content))
        scores.append(self._analyze_vocabulary(content))
        scores.append(self._analyze_coherence(content))
        
        return sum(scores) / len(scores)
    
    def _analyze_length(self, content: str) -> float:
        """Analyze content length"""
        length = len(content)
        
        if length < self.min_length:
            return length / self.min_length
        elif length > self.max_length:
            return max(0, 1 - (length - self.max_length) / self.max_length)
        elif self.optimal_length[0] <= length <= self.optimal_length[1]:
            return 1.0
        else:
            return 0.8
    
    def _analyze_sentence_structure(self, content: str) -> float:
        """Analyze sentence structure"""
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
    
    def _analyze_vocabulary(self, content: str) -> float:
        """Analyze vocabulary diversity"""
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
    
    def _analyze_coherence(self, content: str) -> float:
        """Analyze text coherence"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.8
        
        coherence_score = 0.8
        
        transition_words = [
            'however', 'therefore', 'consequently', 'furthermore',
            'moreover', 'in addition', 'meanwhile', 'otherwise',
            'thus', 'hence', 'accordingly', 'nevertheless',
            '但是', '因此', '所以', '此外', '而且', '同时', '否则',
            '于是', '从而', '然而', '不过'
        ]
        
        has_transitions = any(
            any(word in sentence.lower() for word in transition_words)
            for sentence in sentences
        )
        
        if has_transitions:
            coherence_score += 0.2
        
        return min(1.0, coherence_score)
