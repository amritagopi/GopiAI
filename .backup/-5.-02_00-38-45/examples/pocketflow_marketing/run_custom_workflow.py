#!/usr/bin/env python3
"""
Custom marketing workflow script using the PocketFlow framework.

This script demonstrates how to run a marketing workflow with custom parameters.
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
    linkedin = ChannelAdapterNode(channel="linkedin")
    twitter = ChannelAdapterNode(channel="twitter")
    
    # Create analytics node
    analytics = AnalyticsNode(analytics_type="performance")
    
    # Create workflow using the orchestrator
    workflow = orchestrator.create_content_creation_workflow(
        research_node=research,
        generation_node=generation,
        optimization_node=optimization
    )
    
    # Add distribution and analytics to the workflow
    optimization.add_successor(website)
    website.add_successor(email)
    email.add_successor(linkedin)
    linkedin.add_successor(twitter)
    twitter.add_successor(analytics)
    
    return workflow


def main():
    """Run the custom marketing workflow."""
    print("\n=== Custom Marketing Workflow with Specific Parameters ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create a custom workflow
    print("Creating custom marketing workflow...")
    workflow = create_custom_workflow(orchestrator)
    
    # Initialize the store with specific parameters
    store = {
        # Content Topic and Type
        "topic": "AI-Powered Personalization in E-commerce",
        "content_type": "blog post",
        "target_audience": "e-commerce managers and digital marketers",
        
        # Content Style and Format
        "tone": "professional with actionable insights",
        "length": "medium",  # Options: short, medium, long
        
        # Research Parameters
        "research_type": "comprehensive",  # Options: basic, keyword, comprehensive
        "depth": "detailed",  # Options: basic, detailed, comprehensive
        
        # Optimization Goals
        "optimization_type": "seo",  # Options: seo, readability, conversion, all
        
        # Distribution Channels
        "channels": ["website", "email", "linkedin", "twitter"],
        
        # Analytics Parameters
        "metrics": ["views", "engagement", "conversion", "sharing"],
        "time_period": "next_month"
    }
    
    # Run the workflow
    print("\nRunning marketing workflow with custom parameters...")
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
        print(f"\n{content[:300]}...\n")
    else:
        print(f"\n{str(result.get('generated_content', ''))[:300]}...\n")
    
    # Optimization results
    print("\n--- Optimized Content ---")
    optimized_content = result.get('optimized_content', '')
    if isinstance(optimized_content, dict):
        content_str = optimized_content.get('optimized_content', '')
    else:
        content_str = str(optimized_content)
    print(f"\n{content_str[:300]}...\n")
    
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
    
    print("\n=== End of Custom Workflow ===\n")
    
    # Save the full output to a file
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "marketing_workflow_output.md")
    
    with open(output_file, "w") as f:
        f.write("# Marketing Workflow Output\n\n")
        
        # Research results
        f.write("## Research Results\n\n")
        f.write(f"**Keywords:** {', '.join(research_results.get('keywords', []))}\n\n")
        f.write(f"**Trends:** {', '.join(research_results.get('trends', []))}\n\n")
        f.write(f"**Sources:** {', '.join(research_results.get('sources', []))}\n\n")
        
        # Generated content
        f.write("## Generated Content\n\n")
        if "generated_content" in result and isinstance(result["generated_content"], dict):
            content = result["generated_content"].get("generated_content", "")
            f.write(f"{content}\n\n")
        else:
            f.write(f"{str(result.get('generated_content', ''))}\n\n")
        
        # Optimized content
        f.write("## Optimized Content\n\n")
        f.write(f"{content_str}\n\n")
        
        f.write("### Optimization Recommendations\n\n")
        for rec in result.get("optimization_recommendations", []):
            f.write(f"- {rec}\n")
        f.write("\n")
        
        # Channel adaptations
        f.write("## Channel Adaptations\n\n")
        for channel, content in result.get("channel_adaptations", {}).items():
            f.write(f"### {channel.upper()}\n\n")
            f.write(f"{content}\n\n")
        
        # Analytics results
        f.write("## Analytics Results\n\n")
        f.write(f"**Metrics:** {', '.join(analytics_results.get('metrics', []))}\n\n")
        
        f.write("### Insights\n\n")
        for insight in result.get("analytics_insights", []):
            f.write(f"- {insight}\n")
    
    print(f"\nFull output saved to: {output_file}")


if __name__ == "__main__":
    main()
