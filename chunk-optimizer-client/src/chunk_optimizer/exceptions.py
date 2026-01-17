"""Exceptions for Chunk Optimizer Client"""


class ChunkOptimizerError(Exception):
    """Base exception for Chunk Optimizer errors"""
    pass


class AuthenticationError(ChunkOptimizerError):
    """Authentication failed"""
    pass


class RateLimitError(ChunkOptimizerError):
    """Rate limit exceeded"""
    pass


class NetworkError(ChunkOptimizerError):
    """Network error occurred"""
    pass


class ValidationError(ChunkOptimizerError):
    """Validation error"""
    pass
