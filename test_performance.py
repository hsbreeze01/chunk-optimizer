"""Performance test for chunk optimizer"""
import asyncio
import time
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chunk-optimizer-service', 'src'))

# Use relative imports
import core.optimizer as optimizer_module
import api.rest.schemas as schemas_module

Optimizer = optimizer_module.Optimizer
Chunk = schemas_module.Chunk
AnalysisOptions = schemas_module.AnalysisOptions


def generate_test_chunk(length: int) -> str:
    """Generate test chunk content"""
    words = ["测试", "内容", "优化", "分析", "质量", "冗余", "大小", "相似度", "chunk", "optimizer"]
    content = ""
    for i in range(length):
        content += words[i % len(words)] + " "
        if i % 20 == 0:
            content += ". "
    return content


async def test_single_chunk_performance():
    """Test single chunk performance"""
    print("\n=== 单个 Chunk 性能测试 ===")
    
    optimizer = Optimizer()
    test_content = generate_test_chunk(500)
    
    # Warm up
    await optimizer.analyze_chunk("warmup", test_content, domain="default")
    
    # Test with caching
    times = []
    for i in range(10):
        start = time.time()
        result = await optimizer.analyze_chunk(f"chunk_{i}", test_content, domain="default")
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"平均耗时: {avg_time*1000:.2f}ms")
    print(f"最小耗时: {min_time*1000:.2f}ms")
    print(f"最大耗时: {max_time*1000:.2f}ms")
    print(f"质量分数: {result.metrics.quality_score:.3f}")
    print(f"冗余分数: {result.metrics.redundancy_score:.3f}")
    print(f"大小分数: {result.metrics.size_score:.3f}")
    print(f"相似度分数: {result.metrics.similarity_score:.3f}")
    print(f"综合分数: {result.metrics.overall_score:.3f}")


async def test_batch_performance():
    """Test batch performance with concurrent processing"""
    print("\n=== 批量 Chunk 性能测试 ===")
    
    optimizer = Optimizer()
    
    # Generate test chunks
    chunks = []
    for i in range(100):
        content = generate_test_chunk(300 + i * 10)
        chunks.append(Chunk(
            chunk_id=f"chunk_{i}",
            content=content,
            metadata={"index": i}
        ))
    
    # Test batch processing
    start = time.time()
    result = await optimizer.analyze_document(
        document_id="test_doc",
        chunks=chunks,
        options=AnalysisOptions(),
        domain="default"
    )
    end = time.time()
    
    total_time = end - start
    avg_time_per_chunk = total_time / len(chunks)
    throughput = len(chunks) / total_time
    
    print(f"总耗时: {total_time*1000:.2f}ms")
    print(f"平均每个 Chunk: {avg_time_per_chunk*1000:.2f}ms")
    print(f"吞吐量: {throughput:.2f} chunks/s")
    print(f"优化建议总数: {result.total}")
    print(f"高优先级建议: {result.high_priority}")


async def test_domain_performance():
    """Test performance across different domains"""
    print("\n=== 不同领域性能测试 ===")
    
    optimizer = Optimizer()
    test_content = generate_test_chunk(800)
    
    domains = ["default", "operations", "ecommerce", "medical"]
    
    for domain in domains:
        start = time.time()
        result = await optimizer.analyze_chunk(
            chunk_id=f"test_{domain}",
            content=test_content,
            domain=domain
        )
        end = time.time()
        
        print(f"\n{domain.upper()} 领域:")
        print(f"  耗时: {(end-start)*1000:.2f}ms")
        print(f"  质量分数: {result.metrics.quality_score:.3f}")
        print(f"  冗余分数: {result.metrics.redundancy_score:.3f}")
        print(f"  大小分数: {result.metrics.size_score:.3f}")
        print(f"  相似度分数: {result.metrics.similarity_score:.3f}")
        print(f"  综合分数: {result.metrics.overall_score:.3f}")


async def test_cache_effectiveness():
    """Test cache effectiveness"""
    print("\n=== 缓存效果测试 ===")
    
    optimizer = Optimizer()
    test_content = generate_test_chunk(500)
    
    # First call (cache miss)
    start = time.time()
    result1 = await optimizer.analyze_chunk("cache_test", test_content, domain="default")
    first_call_time = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    result2 = await optimizer.analyze_chunk("cache_test", test_content, domain="default")
    second_call_time = time.time() - start
    
    speedup = first_call_time / second_call_time if second_call_time > 0 else 0
    
    print(f"首次调用（缓存未命中）: {first_call_time*1000:.2f}ms")
    print(f"二次调用（缓存命中）: {second_call_time*1000:.2f}ms")
    print(f"加速比: {speedup:.2f}x")
    print(f"结果一致性: {result1.metrics == result2.metrics}")


async def main():
    """Run all performance tests"""
    print("=" * 60)
    print("Chunk Optimizer 性能测试")
    print("=" * 60)
    
    await test_single_chunk_performance()
    await test_batch_performance()
    await test_domain_performance()
    await test_cache_effectiveness()
    
    print("\n" + "=" * 60)
    print("性能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
