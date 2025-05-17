#!/usr/bin/env python3
"""
Complete example of PocketFlow marketing workflow integration.

This script demonstrates a complete marketing workflow using the fixed
implementation of PocketFlow integration, showing how to create and
execute a marketing automation workflow from research to analytics.
"""
import sys
import os
from typing import Dict, Any

# Add parent directory to path so Python can find the app module
sys.path.append('/Users/helenazhang/manus')

# Import the fixed marketing orchestrator
from app.marketing.fixed_orchestrator import MarketingOrchestrator
from app.marketing.fixed_nodes import (
    ResearchNode,
    ContentGenerationNode,
    ContentOptimizationNode,
    ChannelAdapterNode,
    AnalyticsNode
)


def create_custom_workflow(orchestrator):
    """Create a custom marketing workflow with specific configurations."""
    # Create custom nodes with specific configurations
    research = ResearchNode(max_retries=2)
    generation = ContentGenerationNode(max_retries=2)
    optimization = ContentOptimizationNode(optimization_type="seo", max_retries=2)
    
    # Create channel adapters for different platforms
    website = ChannelAdapterNode(channel="website")
    email = ChannelAdapterNode(channel="email")
    social = ChannelAdapterNode(channel="social_media")
    
    # Create analytics node
    analytics = AnalyticsNode(analytics_type="performance")
    
    # Create workflow using the orchestrator
    workflow = orchestrator.create_content_creation_workflow(
        research_node=research,
        generation_node=generation,
        optimization_node=optimization
    )
    
    # Add distribution and analytics to the workflow
    # Note: This is a manual addition, not using the orchestrator's methods
    optimization.add_successor(website)
    website.add_successor(email)
    email.add_successor(social)
    social.add_successor(analytics)
    
    return workflow


def main():
    """Run the complete marketing workflow example."""
    print("\n=== Complete PocketFlow Marketing Workflow Example ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create a custom workflow
    print("Creating custom marketing workflow...")
    workflow = create_custom_workflow(orchestrator)
    
    # Initial shared state
    store = {
        "topic": "AI in Marketing Automation",
        "content_type": "blog post",
        "target_audience": "marketing professionals",
        "tone": "professional",
        "length": "medium"
    }
    
    # Run the workflow
    print("\nRunning marketing workflow...")
    result = workflow.run(store)
    
    # Display final results
    print("\nWorkflow completed!")
    
    # Research results
    print("\n--- Research Results ---")
    research_results = result.get("research_results", {})
    print(f"Keywords: {research_results.get('keywords', [])}")
    print(f"Trends: {research_results.get('trends', [])}")
    
    # Content generation results
    print("\n--- Generated Content ---")
    if "generated_content" in result and isinstance(result["generated_content"], dict):
        content = result["generated_content"].get("generated_content", "")
        print(f"\n{content[:200]}...\n")
    else:
        print(f"\n{str(result.get('generated_content', ''))[:200]}...\n")
    
    # Optimization results
    print("\n--- Optimized Content ---")
    optimized_content = result.get('optimized_content', '')
    if isinstance(optimized_content, dict):
        content_str = optimized_content.get('optimized_content', '')
    else:
        content_str = str(optimized_content)
    print(f"\n{content_str[:200]}...\n")
    
    print("Optimization recommendations:")
    for rec in result.get("optimization_recommendations", []):
        print(f"- {rec}")
    
    # Channel adaptations
    print("\n--- Channel Adaptations ---")
    for channel, content in result.get("channel_adaptations", {}).items():
        print(f"\n{channel.upper()}:")
        print(f"{content[:100]}...")
    
    # Analytics results
    print("\n--- Analytics Results ---")
    analytics_results = result.get("analytics_results", {})
    print(f"Metrics: {analytics_results.get('metrics', [])}")
    
    print("\nInsights:")
    for insight in result.get("analytics_insights", []):
        print(f"- {insight}")
    
    print("\n=== End of Example ===\n")


if __name__ == "__main__":
    main()
