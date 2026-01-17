"""Chunk Optimizer Client"""
import asyncio
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

import aiohttp
from loguru import logger

from .models import (
    Optimization,
    Metrics,
    OptimizationOptions,
    BatchResult
)
from .exceptions import (
    ChunkOptimizerError,
    AuthenticationError,
    RateLimitError,
    NetworkError
)


class ChunkOptimizerClient:
    """Async Chunk Optimizer Client"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        enable_cache: bool = True,
        cache_ttl: int = 3600
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple] = {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self):
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Content-Type": "application/json"
                }
            )
    
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self._session.request(method, url, json=data) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status != 200:
                    error_text = await response.text()
                    raise ChunkOptimizerError(f"API error: {error_text}")
                
                return await response.json()
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        if not self.enable_cache:
            return None
        
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return data
            else:
                del self._cache[key]
        
        return None
    
    def _set_cache(self, key: str, data: Any):
        if self.enable_cache:
            self._cache[key] = (data, datetime.now().timestamp())
    
    async def analyze_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[Optimization, Metrics]:
        cache_key = f"chunk:{chunk_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        data = {
            "chunk_id": chunk_id,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = await self._request("POST", "/api/v1/chunks/analyze", data)
        
        optimization = Optimization(**response["optimization"])
        metrics = Metrics(**response["metrics"])
        
        result = (optimization, metrics)
        self._set_cache(cache_key, result)
        
        return result
    
    async def analyze_document(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        options: Optional[OptimizationOptions] = None
    ) -> List[Optimization]:
        data = {
            "document_id": document_id,
            "chunks": chunks,
            "options": options.dict() if options else {}
        }
        
        response = await self._request("POST", "/api/v1/documents/analyze", data)
        
        return [Optimization(**opt) for opt in response["optimizations"]]
    
    async def analyze_batch(
        self,
        items: List[Dict[str, Any]],
        options: Optional[OptimizationOptions] = None
    ) -> BatchResult:
        batch_id = str(uuid.uuid4())
        data = {
            "batch_id": batch_id,
            "items": items,
            "options": options.dict() if options else {}
        }
        
        response = await self._request("POST", "/api/v1/batch/analyze", data)
        
        return BatchResult(
            batch_id=batch_id,
            total=len(items),
            processed=response.get("processed", 0),
            optimizations=[Optimization(**response["optimization"])] if response.get("optimization") else []
        )


class SyncChunkOptimizerClient:
    """Synchronous wrapper for Chunk Optimizer Client"""
    
    def __init__(self, *args, **kwargs):
        self._async_client = ChunkOptimizerClient(*args, **kwargs)
        self._loop = asyncio.get_event_loop()
    
    def analyze_chunk(self, *args, **kwargs):
        return self._loop.run_until_complete(
            self._async_client.analyze_chunk(*args, **kwargs)
        )
    
    def analyze_document(self, *args, **kwargs):
        return self._loop.run_until_complete(
            self._async_client.analyze_document(*args, **kwargs)
        )
    
    def analyze_batch(self, *args, **kwargs):
        return self._loop.run_until_complete(
            self._async_client.analyze_batch(*args, **kwargs)
        )
    
    def close(self):
        self._loop.run_until_complete(self._async_client.close())
