"""API schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalyzeChunkRequest(BaseModel):
    chunk_id: str = Field(..., description="Chunk unique identifier")
    content: str = Field(..., description="Chunk content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Chunk metadata")


class Metrics(BaseModel):
    chunk_id: str
    quality_score: float = Field(ge=0, le=1, description="Quality score (0-1)")
    redundancy_score: float = Field(ge=0, le=1, description="Redundancy score (0-1)")
    size_score: float = Field(ge=0, le=1, description="Size score (0-1)")
    similarity_score: float = Field(ge=0, le=1, description="Similarity score (0-1)")
    overall_score: float = Field(ge=0, le=1, description="Overall score (0-1)")


class Optimization(BaseModel):
    id: str
    chunk_id: str
    type: str = Field(..., description="Optimization type")
    priority: str = Field(..., description="Priority level: low, medium, high")
    title: str
    description: str
    suggested_action: str
    related_chunks: Optional[List[str]] = Field(default_factory=list)
    created_at: datetime
    status: str = Field(default="pending", description="Status: pending, applied, ignored")


class OptimizationResponse(BaseModel):
    optimization: Optimization
    metrics: Metrics


class Chunk(BaseModel):
    chunk_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalysisOptions(BaseModel):
    check_quality: bool = True
    check_redundancy: bool = True
    check_size: bool = True
    check_similarity: bool = True
    similarity_threshold: float = Field(default=0.85, ge=0, le=1)


class AnalyzeDocumentRequest(BaseModel):
    document_id: str = Field(..., description="Document unique identifier")
    chunks: List[Chunk]
    options: Optional[AnalysisOptions] = Field(default_factory=AnalysisOptions)


class OptimizationListResponse(BaseModel):
    optimizations: List[Optimization]
    total: int
    high_priority: int


class BatchItem(BaseModel):
    chunk_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalyzeBatchRequest(BaseModel):
    batch_id: str = Field(..., description="Batch unique identifier")
    items: List[BatchItem]
    options: Optional[AnalysisOptions] = Field(default_factory=AnalysisOptions)


class BatchOptimizationResponse(BaseModel):
    batch_id: str
    item_id: str
    optimization: Optional[Optimization]
    processed: int
    total: int
