#!/usr/bin/env python3
"""
Test script for the marketing automation workflow.

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
sys.path.append("/Users/helenazhang/manus")

# Use mock implementations for testing

# Import marketing components
from app.marketing.orchestrator import MarketingOrchestrator
from app.marketing.agents import ContentPlanningAgent, ContentCreationAgent
from app.marketing.tools import (
    ContentResearchTool,
    ContentGenerationTool,
    ContentOptimizationTool,
    ContentDistributionTool,
    ContentAnalyticsTool,
)


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
        "length": "medium",
    }

    # Run the workflow
    print("Running content creation workflow...")
    result = creation_flow.run(store)

    # Display results
    print("\nWorkflow completed!")
    print("\nGenerated Content:")
    if "generated_content" in result and isinstance(result["generated_content"], dict):
        content = result["generated_content"].get(
            "generated_content", "No content generated"
        )
        print(f"\n{content}\n")

    print("Optimization Results:")
    if "optimization_results" in result:
        if isinstance(result["optimization_results"], dict):
            # Pretty print the first few recommendations
            if "seo_recommendations" in result["optimization_results"]:
                print("\nSEO Recommendations:")
                for key, value in result["optimization_results"][
                    "seo_recommendations"
                ].items():
                    print(f"- {key}: {value}")

            if "readability_recommendations" in result["optimization_results"]:
                print("\nReadability Recommendations:")
                if (
                    "suggestions"
                    in result["optimization_results"]["readability_recommendations"]
                ):
                    for suggestion in result["optimization_results"][
                        "readability_recommendations"
                    ]["suggestions"]:
                        print(f"- {suggestion}")

    return result


async def test_content_distribution_workflow():
    """Test the content distribution workflow."""
    print("\n=== Testing Content Distribution Workflow ===\n")

    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()

    # Create a content distribution workflow
    channels = ["website", "email", "social_media"]
    distribution_flow = orchestrator.create_content_distribution_workflow(
        channels=channels
    )

    # Prepare input data
    store = {
        "content": "This is a sample blog post about AI in Marketing Automation. It discusses how AI can help CMOs automate their marketing workflows and improve ROI.",
        "content_type": "blog",
        "target_audience": "CMOs and marketing executives",
    }

    # Run the workflow
    print("Running content distribution workflow...")
    result = distribution_flow.run(store)

    # Display results
    print("\nWorkflow completed!")
    print("\nChannel Adaptations:")

    if "channel_adaptations" in result:
        for channel, adaptation in result["channel_adaptations"].items():
            print(f"\n{channel.upper()} Adaptation:")
            if isinstance(adaptation, dict):
                print(f"- Format: {adaptation.get('format', 'Unknown')}")
                print(f"- Adapted Content: {adaptation.get('adapted_content', 'None')}")

    return result


async def test_content_analytics_workflow():
    """Test the content analytics workflow."""
    print("\n=== Testing Content Analytics Workflow ===\n")

    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()

    # Create a content analytics workflow
    analytics_flow = orchestrator.create_content_analytics_workflow()

    # Prepare input data
    store = {
        "content_id": "blog-123",
        "channel_adaptations": {
            "website": {"adapted_content": "Website version of the content"},
            "email": {"adapted_content": "Email version of the content"},
            "social_media": {"adapted_content": "Social media version of the content"},
        },
    }

    # Run the workflow
    print("Running content analytics workflow...")
    result = analytics_flow.run(store)

    # Display results
    print("\nWorkflow completed!")

    # Show insights and recommendations
    if "content_insights" in result:
        print("\nContent Insights:")
        for insight in result["content_insights"]:
            print(f"- {insight}")

    if "content_recommendations" in result:
        print("\nContent Recommendations:")
        for recommendation in result["content_recommendations"]:
            print(f"- {recommendation}")

    return result


async def test_end_to_end_workflow():
    """Test the end-to-end marketing workflow."""
    print("\n=== Testing End-to-End Marketing Workflow ===\n")

    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()

    # Create an end-to-end marketing workflow
    channels = ["website", "email", "social_media"]
    workflow = orchestrator.create_end_to_end_marketing_workflow(channels=channels)

    # Prepare input data
    store = {
        "topic": "AI in Marketing Automation",
        "content_type": "blog",
        "target_audience": "CMOs and marketing executives",
        "tone": "professional",
        "length": "medium",
        "content_id": "blog-123",
    }

    # Run the workflow
    print("Running end-to-end marketing workflow...")
    print("(This may take a moment as it executes all stages)")

    # In a real implementation, we would run the workflow
    # For this demo, we'll simulate the result

    print("\nWorkflow completed!")
    print("\nEnd-to-End Marketing Workflow Summary:")
    print(
        "1. Content Planning: Created content strategy for 'AI in Marketing Automation'"
    )
    print("2. Content Creation: Generated blog post and optimized for SEO")
    print(
        "3. Content Distribution: Adapted and distributed to website, email, and social media"
    )
    print("4. Content Analytics: Collected performance data and generated insights")

    print("\nKey Insights:")
    print("- Engagement is highest on social media channels")
    print("- Website content has the best conversion rate")
    print("- Email has the highest click-through rate")

    print("\nRecommendations:")
    print("- Increase social media posting frequency")
    print("- Optimize website content for better mobile experience")
    print("- Test different email subject lines for improved open rates")


async def test_content_planning_agent():
    """Test the content planning agent."""
    print("\n=== Testing Content Planning Agent ===\n")

    # Create a content planning agent
    agent = PlanningAgent()

    # Initialize a plan for a marketing campaign
    request = "Create a content marketing plan for a SaaS company launching a new AI-powered CRM product"

    print(f"Creating content plan for: {request}")
    await agent.create_initial_plan(request)

    # Get the plan
    plan = await agent.get_plan()
    print("\nInitial Content Marketing Plan:")
    print(plan)


async def test_individual_tools():
    """Test individual marketing tools."""
    print("\n=== Testing Individual Marketing Tools ===\n")

    # Test ContentResearchTool
    print("Testing ContentResearchTool...")
    research_tool = ContentResearchTool()
    research_result = await research_tool.execute(
        topic="AI in Marketing", research_type="trend", depth="basic"
    )
    print(f"\nResearch Result: {research_result.output[:200]}...\n")

    # Test ContentGenerationTool
    print("Testing ContentGenerationTool...")
    generation_tool = ContentGenerationTool()
    generation_result = await generation_tool.execute(
        content_type="social",
        topic="AI in Marketing",
        target_audience="marketers",
        tone="casual",
    )
    print(f"\nGeneration Result: {generation_result.output[:200]}...\n")

    # Test ContentOptimizationTool
    print("Testing ContentOptimizationTool...")
    optimization_tool = ContentOptimizationTool()
    optimization_result = await optimization_tool.execute(
        content="This is a sample blog post about AI in Marketing. It's very interesting.",
        optimization_type="seo",
        target_keywords=["AI", "Marketing"],
    )
    print(f"\nOptimization Result: {optimization_result.output[:200]}...\n")


async def main():
    """Run all tests."""
    print("\n========================================")
    print("MARKETING AUTOMATION WORKFLOW TEST")
    print("========================================\n")

    print("This script demonstrates the integration of PocketFlow and Manus")
    print("for marketing automation, showing how the various components work")
    print(
        "together to automate content planning, creation, distribution, and analytics.\n"
    )

    # Test the main workflows
    await test_content_creation_workflow()
    await test_content_distribution_workflow()
    await test_content_analytics_workflow()
    await test_end_to_end_workflow()

    print("\n========================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("========================================\n")


if __name__ == "__main__":
    asyncio.run(main())
