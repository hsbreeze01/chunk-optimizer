"""FastAPI application"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from ..schemas import (
    AnalyzeChunkRequest,
    AnalyzeDocumentRequest,
    AnalyzeBatchRequest,
    OptimizationResponse,
    OptimizationListResponse,
    BatchOptimizationResponse
)
from ...config.settings import settings
from ...core.optimizer import Optimizer


logger.remove()
logger.add(sys.stdout, level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("Starting Chunk Optimizer Service")
    yield
    logger.info("Shutting down Chunk Optimizer Service")


app = FastAPI(
    title="Chunk Optimizer Service",
    description="Optimization service for RAG document chunks",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


optimizer = Optimizer()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}


@app.post(
    "/api/v1/chunks/analyze",
    response_model=OptimizationResponse,
    summary="Analyze single chunk",
    description="Analyze a single chunk and return optimization suggestions"
)
async def analyze_chunk(request: AnalyzeChunkRequest):
    """Analyze single chunk"""
    try:
        result = await optimizer.analyze_chunk(
            chunk_id=request.chunk_id,
            content=request.content,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/v1/documents/analyze",
    response_model=OptimizationListResponse,
    summary="Analyze document chunks",
    description="Analyze all chunks in a document"
)
async def analyze_document(request: AnalyzeDocumentRequest):
    """Analyze document chunks"""
    try:
        result = await optimizer.analyze_document(
            document_id=request.document_id,
            chunks=request.chunks,
            options=request.options
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/v1/batch/analyze",
    response_model=BatchOptimizationResponse,
    summary="Batch analyze chunks",
    description="Batch analyze multiple chunks"
)
async def analyze_batch(request: AnalyzeBatchRequest):
    """Batch analyze chunks"""
    try:
        result = await optimizer.analyze_batch(
            batch_id=request.batch_id,
            items=request.items,
            options=request.options
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
