"""Optimization engine"""
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from functools import lru_cache
from loguru import logger

from api.rest.schemas import (
    Optimization,
    Metrics,
    Chunk,
    AnalysisOptions,
    OptimizationResponse,
    OptimizationListResponse,
    BatchOptimizationResponse,
    BatchItem
)
from algorithms.quality_analyzer import QualityAnalyzer
from algorithms.redundancy_detector import RedundancyDetector
from algorithms.size_analyzer import SizeAnalyzer
from algorithms.similarity_calculator import SimilarityCalculator
from config.domain_config import (
    get_domain_config,
    calculate_overall_score,
    get_optimization_priority,
    DomainConfig
)


class Optimizer:
    """Chunk optimization engine with caching and async support"""
    
    def __init__(self):
        self.quality_analyzer = QualityAnalyzer()
        self.redundancy_detector = RedundancyDetector()
        self.size_analyzer = SizeAnalyzer()
        self.similarity_calculator = SimilarityCalculator()
    
    async def analyze_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        domain: str = "default"
    ) -> OptimizationResponse:
        """Analyze a single chunk"""
        logger.info(f"Analyzing chunk: {chunk_id} with domain: {domain}")
        
        config = get_domain_config(domain)
        
        # Update analyzers with domain config
        self._update_analyzers_config(config)
        
        metrics = self._calculate_metrics(chunk_id, content, config)
        optimizations = self._generate_optimizations(
            chunk_id,
            content,
            metrics,
            config,
            AnalysisOptions()
        )
        
        return OptimizationResponse(
            optimization=optimizations[0] if optimizations else self._create_empty_optimization(chunk_id),
            metrics=metrics
        )
    
    async def analyze_document(
        self,
        document_id: str,
        chunks: List[Chunk],
        options: Optional[AnalysisOptions] = None,
        domain: str = "default"
    ) -> OptimizationListResponse:
        """Analyze all chunks in a document with concurrent processing"""
        logger.info(f"Analyzing document: {document_id} with {len(chunks)} chunks and domain: {domain}")
        
        options = options or AnalysisOptions()
        config = get_domain_config(domain)
        
        # Update analyzers with domain config
        self._update_analyzers_config(config)
        
        # Process chunks concurrently
        tasks = [
            self._analyze_chunk_async(chunk, config, options)
            for chunk in chunks
        ]
        results = await asyncio.gather(*tasks)
        
        all_optimizations = []
        high_priority_count = 0
        
        for optimizations in results:
            for opt in optimizations:
                if opt.priority == "high":
                    high_priority_count += 1
                all_optimizations.append(opt)
        
        return OptimizationListResponse(
            optimizations=all_optimizations,
            total=len(all_optimizations),
            high_priority=high_priority_count
        )
    
    async def analyze_batch(
        self,
        batch_id: str,
        items: List[BatchItem],
        options: Optional[AnalysisOptions] = None,
        domain: str = "default"
    ) -> BatchOptimizationResponse:
        """Batch analyze chunks with concurrent processing"""
        logger.info(f"Analyzing batch: {batch_id} with {len(items)} items and domain: {domain}")
        
        options = options or AnalysisOptions()
        config = get_domain_config(domain)
        
        # Update analyzers with domain config
        self._update_analyzers_config(config)
        
        # Process items concurrently
        tasks = [
            self._analyze_batch_item_async(batch_id, item, config, options, idx)
            for idx, item in enumerate(items)
        ]
        results = await asyncio.gather(*tasks)
        
        return results[0] if results else BatchOptimizationResponse(
            batch_id=batch_id,
            item_id="",
            optimization=None,
            processed=0,
            total=len(items)
        )
    
    def _update_analyzers_config(self, config: DomainConfig):
        """Update all analyzers with domain configuration"""
        self.quality_analyzer = QualityAnalyzer(config)
        self.size_analyzer = SizeAnalyzer(config)
    
    @lru_cache(maxsize=1000)
    def _calculate_metrics(self, chunk_id: str, content: str, config: DomainConfig) -> Metrics:
        """Calculate quality metrics for a chunk using domain configuration with caching"""
        quality_score = self.quality_analyzer.analyze(content)
        redundancy_score = self.redundancy_detector.analyze(content)
        size_score = self.size_analyzer.analyze(content)
        similarity_score = self.similarity_calculator.analyze(content)
        
        overall_score = calculate_overall_score(
            quality_score,
            redundancy_score,
            size_score,
            similarity_score,
            config
        )
        
        return Metrics(
            chunk_id=chunk_id,
            quality_score=quality_score,
            redundancy_score=redundancy_score,
            size_score=size_score,
            similarity_score=similarity_score,
            overall_score=overall_score
        )
    
    async def _analyze_chunk_async(
        self,
        chunk: Chunk,
        config: DomainConfig,
        options: AnalysisOptions
    ) -> List[Optimization]:
        """Analyze a single chunk asynchronously"""
        metrics = self._calculate_metrics(chunk.chunk_id, chunk.content, config)
        return self._generate_optimizations(
            chunk.chunk_id,
            chunk.content,
            metrics,
            config,
            options
        )
    
    async def _analyze_batch_item_async(
        self,
        batch_id: str,
        item: BatchItem,
        config: DomainConfig,
        options: AnalysisOptions,
        idx: int
    ) -> BatchOptimizationResponse:
        """Analyze a batch item asynchronously"""
        metrics = self._calculate_metrics(item.chunk_id, item.content, config)
        optimizations = self._generate_optimizations(
            item.chunk_id,
            item.content,
            metrics,
            config,
            options
        )
        
        return BatchOptimizationResponse(
            batch_id=batch_id,
            item_id=item.chunk_id,
            optimization=optimizations[0] if optimizations else None,
            processed=idx + 1,
            total=0  # Will be updated by caller
        )
    
    def _generate_optimizations(
        self,
        chunk_id: str,
        content: str,
        metrics: Metrics,
        config: DomainConfig,
        options: Optional[AnalysisOptions] = None
    ) -> List[Optimization]:
        """Generate optimization suggestions based on metrics using domain configuration"""
        options = options or AnalysisOptions()
        optimizations = []
        
        if options.check_quality:
            priority = get_optimization_priority(
                metrics.quality_score,
                config.quality_threshold
            )
            if priority in ["HIGH", "MEDIUM"]:
                optimizations.append(Optimization(
                    id=str(uuid.uuid4()),
                    chunk_id=chunk_id,
                    type="quality",
                    priority=priority,
                    title="Chunk quality needs improvement",
                    description=f"Quality score is {metrics.quality_score:.2f}, which is below recommended threshold of {config.quality_threshold}",
                    suggested_action="Review and rewrite the chunk to improve clarity, coherence, and completeness",
                    created_at=datetime.utcnow()
                ))
        
        if options.check_redundancy:
            priority = get_optimization_priority(
                metrics.redundancy_score,
                config.redundancy_threshold,
                high_threshold=config.redundancy_threshold * 1.2
            )
            if priority in ["HIGH", "MEDIUM"]:
                optimizations.append(Optimization(
                    id=str(uuid.uuid4()),
                    chunk_id=chunk_id,
                    type="redundancy",
                    priority=priority,
                    title="Redundant content detected",
                    description=f"Redundancy score is {metrics.redundancy_score:.2f}, indicating significant repetitive content",
                    suggested_action="Remove or consolidate redundant information to improve efficiency",
                    created_at=datetime.utcnow()
                ))
        
        if options.check_size:
            priority = get_optimization_priority(
                metrics.size_score,
                config.size_threshold
            )
            if priority in ["HIGH", "MEDIUM"]:
                optimizations.append(Optimization(
                    id=str(uuid.uuid4()),
                    chunk_id=chunk_id,
                    type="size",
                    priority=priority,
                    title="Chunk size is suboptimal",
                    description=f"Size score is {metrics.size_score:.2f}, indicating that chunk may be too short or too long",
                    suggested_action=f"Adjust chunk size to optimal range ({config.optimal_length[0]}-{config.optimal_length[1]} characters)",
                    created_at=datetime.utcnow()
                ))
        
        if options.check_similarity:
            priority = get_optimization_priority(
                metrics.similarity_score,
                config.similarity_threshold,
                high_threshold=config.similarity_threshold * 1.1
            )
            if priority in ["HIGH", "MEDIUM"]:
                optimizations.append(Optimization(
                    id=str(uuid.uuid4()),
                    chunk_id=chunk_id,
                    type="similarity",
                    priority=priority,
                    title="Highly similar content detected",
                    description=f"Similarity score is {metrics.similarity_score:.2f}, indicating potential duplicate content",
                    suggested_action="Review and merge with similar chunks to avoid redundancy",
                    created_at=datetime.utcnow()
                ))
        
        return optimizations
    
    def _create_empty_optimization(self, chunk_id: str) -> Optimization:
        """Create an empty optimization when no issues are found"""
        return Optimization(
            id=str(uuid.uuid4()),
            chunk_id=chunk_id,
            type="info",
            priority="low",
            title="No optimization needed",
            description="This chunk meets all quality standards",
            suggested_action="No action required",
            created_at=datetime.utcnow(),
            status="applied"
        )
