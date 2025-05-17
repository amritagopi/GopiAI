#!/usr/bin/env python3
"""
Test script for the fixed marketing automation workflow.

This script demonstrates the integration of PocketFlow and Manus for
marketing automation, showing how the various components work together
to automate content planning, creation, distribution, and analytics.
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add parent directory to path so Python can find the app module
sys.path.append('/Users/helenazhang/manus')

# Import marketing components
from app.marketing.fixed_orchestrator import MarketingOrchestrator


async def test_content_creation_workflow():
    """Test the content creation workflow."""
    print("\n=== Testing Content Creation Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create a content creation workflow
    creation_flow = orchestrator.create_content_creation_workflow()
    
    # Prepare input data
    store = {
        "topic": "AI in Marketing Automation",
        "content_type": "blog",
        "target_audience": "CMOs and marketing executives",
        "tone": "professional",
        "length": "medium"
    }
    
    # Run the workflow
    print("Running content creation workflow...")
    result = creation_flow.run(store)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nGenerated Content:")
    if "generated_content" in result and isinstance(result["generated_content"], dict):
        content = result["generated_content"].get("generated_content", "No content generated")
        print(f"\n{content}\n")
    else:
        print(f"\n{result.get('generated_content', 'No content generated')}\n")
    
    print("Optimization recommendations:")
    for rec in result.get("optimization_recommendations", []):
        print(f"- {rec}")
    
    return result


async def test_content_distribution_workflow():
    """Test the content distribution workflow."""
    print("\n=== Testing Content Distribution Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create a content distribution workflow
    channels = ["website", "email", "social_media"]
    distribution_flow = orchestrator.create_content_distribution_workflow(channels=channels)
    
    # Prepare input data with generated content
    store = {
        "generated_content": "This is a sample blog post about AI in marketing automation.",
        "optimized_content": "This is an optimized sample blog post about AI in marketing automation.",
        "target_audience": "marketing professionals"
    }
    
    # Run the workflow
    print("Running content distribution workflow...")
    result = distribution_flow.run(store)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nChannel Adaptations:")
    for channel, content in result.get("channel_adaptations", {}).items():
        print(f"\n{channel.upper()}:")
        print(f"{content[:100]}...")
    
    return result


async def test_content_analytics_workflow():
    """Test the content analytics workflow."""
    print("\n=== Testing Content Analytics Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create a content analytics workflow
    analytics_flow = orchestrator.create_content_analytics_workflow()
    
    # Prepare input data with channel adaptations
    store = {
        "content_id": "blog-123",
        "channel_adaptations": {
            "website": "Website content...",
            "email": "Email content...",
            "social_media": "Social media content..."
        },
        "metrics": ["views", "engagement", "conversion"],
        "time_period": "last_month"
    }
    
    # Run the workflow
    print("Running content analytics workflow...")
    result = analytics_flow.run(store)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nAnalytics Results:")
    if "analytics_results" in result:
        print(f"\nMetrics: {result['analytics_results'].get('metrics', [])}")
        print("\nInsights:")
        for insight in result.get("analytics_insights", []):
            print(f"- {insight}")
    
    return result


async def test_end_to_end_workflow():
    """Test the end-to-end marketing workflow."""
    print("\n=== Testing End-to-End Marketing Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Create an end-to-end marketing workflow
    channels = ["website", "email", "social_media"]
    end_to_end_flow = orchestrator.create_end_to_end_marketing_workflow(channels=channels)
    
    # Prepare input data
    store = {
        "topic": "AI in Marketing Automation",
        "content_type": "blog",
        "target_audience": "marketing professionals",
        "tone": "professional",
        "length": "medium"
    }
    
    # Run the workflow
    print("Running end-to-end marketing workflow...")
    result = end_to_end_flow.run(store)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nGenerated Content:")
    if "generated_content" in result and isinstance(result["generated_content"], dict):
        content = result["generated_content"].get("generated_content", "No content generated")
        print(f"\n{content[:200]}...\n")
    else:
        print(f"\n{str(result.get('generated_content', 'No content generated'))[:200]}...\n")
    
    print("Channel Adaptations:")
    for channel, content in result.get("channel_adaptations", {}).items():
        print(f"\n{channel.upper()}:")
        print(f"{content[:100]}...")
    
    print("\nAnalytics Insights:")
    for insight in result.get("analytics_insights", []):
        print(f"- {insight}")
    
    return result


async def main():
    """Run all tests."""
    print("\n========================================")
    print("FIXED MARKETING AUTOMATION WORKFLOW TEST")
    print("========================================")
    print("\nThis script demonstrates the integration of PocketFlow and Manus")
    print("for marketing automation, showing how the various components work")
    print("together to automate content planning, creation, distribution, and analytics.")
    
    # Test content creation workflow
    await test_content_creation_workflow()
    
    # Test content distribution workflow
    await test_content_distribution_workflow()
    
    # Test content analytics workflow
    await test_content_analytics_workflow()
    
    # Test end-to-end workflow
    await test_end_to_end_workflow()


if __name__ == "__main__":
    asyncio.run(main())
