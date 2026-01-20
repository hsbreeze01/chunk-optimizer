# -*- coding: utf-8 -*-
"""
Domain Configuration Usage Example
Shows how to use different configurations for different domains (operations, ecommerce, medical)
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from chunk_optimizer_service.src.config.domain_config import (
    get_domain_config,
    calculate_overall_score,
    get_optimization_priority,
    DOMAIN_CONFIGS
)


def example_operations_domain():
    """Operations domain configuration example"""
    print("=" * 60)
    print("Operations Domain Configuration Example")
    print("=" * 60)
    
    config = get_domain_config("operations")
    
    print("\nWeight Configuration:")
    print("  Quality Weight: {}".format(config.quality_weight))
    print("  Redundancy Weight: {}".format(config.redundancy_weight))
    print("  Size Weight: {}".format(config.size_weight))
    print("  Similarity Weight: {}".format(config.similarity_weight))
    
    print("\nThreshold Configuration:")
    print("  Quality Threshold: {}".format(config.quality_threshold))
    print("  Redundancy Threshold: {}".format(config.redundancy_threshold))
    print("  Size Threshold: {}".format(config.size_threshold))
    print("  Similarity Threshold: {}".format(config.similarity_threshold))
    
    print("\nAlgorithm Parameters:")
    print("  Min Length: {}".format(config.min_length))
    print("  Max Length: {}".format(config.max_length))
    print("  Optimal Length: {}".format(config.optimal_length))
    
    # Simulated analysis results
    quality_score = 0.65
    redundancy_score = 0.35
    size_score = 0.75
    similarity_score = 0.12
    
    overall = calculate_overall_score(
        quality_score,
        redundancy_score,
        size_score,
        similarity_score,
        config
    )
    
    print("\nOverall Score: {:.2f}".format(overall))
    
    # Determine optimization priority
    quality_priority = get_optimization_priority(
        quality_score,
        config.quality_threshold
    )
    print("Quality Optimization Priority: {}".format(quality_priority))


def example_ecommerce_domain():
    """E-commerce domain configuration example"""
    print("\n" + "=" * 60)
    print("E-commerce Domain Configuration Example")
    print("=" * 60)
    
    config = get_domain_config("ecommerce")
    
    print("\nWeight Configuration:")
    print("  Quality Weight: {}".format(config.quality_weight))
    print("  Redundancy Weight: {}".format(config.redundancy_weight))
    print("  Size Weight: {}".format(config.size_weight))
    print("  Similarity Weight: {}".format(config.similarity_weight))
    
    print("\nThreshold Configuration:")
    print("  Quality Threshold: {}".format(config.quality_threshold))
    print("  Redundancy Threshold: {}".format(config.redundancy_threshold))
    print("  Size Threshold: {}".format(config.size_threshold))
    print("  Similarity Threshold: {}".format(config.similarity_threshold))
    
    print("\nAlgorithm Parameters:")
    print("  Min Length: {}".format(config.min_length))
    print("  Max Length: {}".format(config.max_length))
    print("  Optimal Length: {}".format(config.optimal_length))
    
    # Simulated analysis results
    quality_score = 0.55
    redundancy_score = 0.45
    size_score = 0.65
    similarity_score = 0.25
    
    overall = calculate_overall_score(
        quality_score,
        redundancy_score,
        size_score,
        similarity_score,
        config
    )
    
    print("\nOverall Score: {:.2f}".format(overall))
    
    # Determine optimization priority
    similarity_priority = get_optimization_priority(
        similarity_score,
        config.similarity_threshold
    )
    print("Similarity Optimization Priority: {}".format(similarity_priority))


def example_medical_domain():
    """Medical domain configuration example"""
    print("\n" + "=" * 60)
    print("Medical Domain Configuration Example")
    print("=" * 60)
    
    config = get_domain_config("medical")
    
    print("\nWeight Configuration:")
    print("  Quality Weight: {}".format(config.quality_weight))
    print("  Redundancy Weight: {}".format(config.redundancy_weight))
    print("  Size Weight: {}".format(config.size_weight))
    print("  Similarity Weight: {}".format(config.similarity_weight))
    
    print("\nThreshold Configuration:")
    print("  Quality Threshold: {}".format(config.quality_threshold))
    print("  Redundancy Threshold: {}".format(config.redundancy_threshold))
    print("  Size Threshold: {}".format(config.size_threshold))
    print("  Similarity Threshold: {}".format(config.similarity_threshold))
    
    print("\nAlgorithm Parameters:")
    print("  Min Length: {}".format(config.min_length))
    print("  Max Length: {}".format(config.max_length))
    print("  Optimal Length: {}".format(config.optimal_length))
    
    # Simulated analysis results
    quality_score = 0.75
    redundancy_score = 0.25
    size_score = 0.85
    similarity_score = 0.08
    
    overall = calculate_overall_score(
        quality_score,
        redundancy_score,
        size_score,
        similarity_score,
        config
    )
    
    print("\nOverall Score: {:.2f}".format(overall))
    
    # Determine optimization priority
    quality_priority = get_optimization_priority(
        quality_score,
        config.quality_threshold
    )
    redundancy_priority = get_optimization_priority(
        redundancy_score,
        config.redundancy_threshold
    )
    print("Quality Optimization Priority: {}".format(quality_priority))
    print("Redundancy Optimization Priority: {}".format(redundancy_priority))


def example_comparison():
    """Cross-domain comparison example"""
    print("\n" + "=" * 60)
    print("Cross-Domain Configuration Comparison")
    print("=" * 60)
    
    # Same analysis results
    quality_score = 0.65
    redundancy_score = 0.35
    size_score = 0.75
    similarity_score = 0.12
    
    print("\nAnalysis Results:")
    print("  Quality Score: {}".format(quality_score))
    print("  Redundancy Score: {}".format(redundancy_score))
    print("  Size Score: {}".format(size_score))
    print("  Similarity Score: {}".format(similarity_score))
    
    print("\nOverall Score Comparison:")
    for domain_name, config in DOMAIN_CONFIGS.items():
        overall = calculate_overall_score(
            quality_score,
            redundancy_score,
            size_score,
            similarity_score,
            config
        )
        print("  {}: {:.2f}".format(domain_name, overall))


if __name__ == "__main__":
    example_operations_domain()
    example_ecommerce_domain()
    example_medical_domain()
    example_comparison()
