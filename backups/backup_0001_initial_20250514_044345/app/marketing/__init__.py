"""
Marketing automation module for PocketFlow and Manus integration.

This module provides specialized tools, agents, and flows for marketing automation,
leveraging the combined capabilities of PocketFlow's structured workflows and
Manus's agent-based planning.
"""

# Import core components
from app.marketing.orchestrator import MarketingOrchestrator
from app.marketing.agents import ContentPlanningAgent, ContentCreationAgent
from app.marketing.tools import (
    ContentResearchTool,
    ContentGenerationTool,
    ContentOptimizationTool,
    ContentDistributionTool,
    ContentAnalyticsTool
)
from app.marketing.flows import (
    ContentPlanningFlow,
    ContentCreationFlow,
    ContentDistributionFlow,
    ContentAnalyticsFlow
)
from app.marketing.nodes import (
    ResearchNode,
    ContentGenerationNode,
    ContentOptimizationNode,
    ChannelAdapterNode,
    AnalyticsNode
)

__all__ = [
    'MarketingOrchestrator',
    'ContentPlanningAgent',
    'ContentCreationAgent',
    'ContentResearchTool',
    'ContentGenerationTool',
    'ContentOptimizationTool',
    'ContentDistributionTool',
    'ContentAnalyticsTool',
    'ContentPlanningFlow',
    'ContentCreationFlow',
    'ContentDistributionFlow',
    'ContentAnalyticsFlow',
    'ResearchNode',
    'ContentGenerationNode',
    'ContentOptimizationNode',
    'ChannelAdapterNode',
    'AnalyticsNode'
]
