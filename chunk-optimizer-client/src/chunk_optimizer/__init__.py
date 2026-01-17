"""Chunk Optimizer Client SDK"""
from .client import ChunkOptimizerClient, SyncChunkOptimizerClient
from .models import Optimization, Metrics, OptimizationOptions, BatchResult
from .exceptions import ChunkOptimizerError, AuthenticationError, RateLimitError

__version__ = "0.1.0"
__all__ = [
    "ChunkOptimizerClient",
    "SyncChunkOptimizerClient",
    "Optimization",
    "Metrics",
    "OptimizationOptions",
    "BatchResult",
    "ChunkOptimizerError",
    "AuthenticationError",
    "RateLimitError",
]
