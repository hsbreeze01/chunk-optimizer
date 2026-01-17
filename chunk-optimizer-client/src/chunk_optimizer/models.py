"""Data models for Chunk Optimizer Client"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Optimization(BaseModel):
    """Optimization suggestion"""
    id: str
    chunk_id: str
    type: str
    priority: str = Field(..., description="Priority: low, medium, high")
    title: str
    description: str
    suggested_action: str
    related_chunks: Optional[List[str]] = Field(default_factory=list)
    created_at: datetime
    status: str = Field(default="pending")


class Metrics(BaseModel):
    """Quality metrics for a chunk"""
    chunk_id: str
    quality_score: float = Field(ge=0, le=1)
    redundancy_score: float = Field(ge=0, le=1)
    size_score: float = Field(ge=0, le=1)
    similarity_score: float = Field(ge=0, le=1)
    overall_score: float = Field(ge=0, le=1)


class OptimizationOptions(BaseModel):
    """Options for optimization analysis"""
    check_quality: bool = True
    check_redundancy: bool = True
    check_size: bool = True
    check_similarity: bool = True
    similarity_threshold: float = Field(default=0.85, ge=0, le=1)


class BatchResult(BaseModel):
    """Result of batch optimization"""
    batch_id: str
    total: int
    processed: int
    optimizations: List[Optimization]
    failed: Optional[List[str]] = Field(default_factory=list)
