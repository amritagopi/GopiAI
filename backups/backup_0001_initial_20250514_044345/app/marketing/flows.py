"""
Marketing-specific flows for PocketFlow integration.

This module provides specialized flows for marketing tasks that can be used
to orchestrate marketing automation workflows, focusing on content planning,
creation, distribution, and analytics.
"""
from typing import Any, Dict, List, Optional

from pocketflow_framework import Flow, Node

from app.flow.base import BaseFlow
from app.flow.planning import PlanningFlow
from app.agent.planning import PlanningAgent
from app.marketing.agents import ContentPlanningAgent, ContentCreationAgent
from app.marketing.nodes import (
    ResearchNode,
    ContentGenerationNode,
    ContentOptimizationNode,
    ChannelAdapterNode,
    AnalyticsNode
)


class ContentPlanningFlow(PlanningFlow):
    """
    Flow for content planning and strategy.
    
    This flow uses a ContentPlanningAgent to develop content strategies,
    editorial calendars, and marketing plans.
    """
    
    def __init__(
        self,
        agent: Optional[PlanningAgent] = None,
        name: str = "ContentPlanningFlow"
    ):
        """
        Initialize a content planning flow.
        
        Args:
            agent: Agent responsible for planning (defaults to ContentPlanningAgent)
            name: Name for the flow
        """
        # Use ContentPlanningAgent by default
        planning_agent = agent or ContentPlanningAgent()
        
        # Initialize with the planning agent
        super().__init__(
            agent=planning_agent,
            name=name
        )


class ContentCreationFlow(Flow):
    """
    Flow for content creation and optimization.
    
    This flow orchestrates research, generation, and optimization nodes
    to create high-quality marketing content.
    """
    
    def __init__(
        self,
        content_type: str = "blog",
        include_research: bool = True,
        include_optimization: bool = True,
        name: str = "ContentCreationFlow"
    ):
        """
        Initialize a content creation flow.
        
        Args:
            content_type: Type of content to create
            include_research: Whether to include a research node
            include_optimization: Whether to include an optimization node
            name: Name for the flow
        """
        # Create nodes
        nodes = []
        
        if include_research:
            nodes.append(ResearchNode())
            
        nodes.append(ContentGenerationNode(content_type=content_type))
        
        if include_optimization:
            nodes.append(ContentOptimizationNode())
        
        # Initialize the flow
        super().__init__(nodes=nodes, name=name)
        
        # Connect nodes sequentially
        for i in range(len(nodes) - 1):
            self.connect(nodes[i].name, nodes[i + 1].name)


class ContentDistributionFlow(Flow):
    """
    Flow for content distribution across multiple channels.
    
    This flow adapts content for different channels and manages
    the distribution process.
    """
    
    def __init__(
        self,
        channels: List[str] = None,
        name: str = "ContentDistributionFlow"
    ):
        """
        Initialize a content distribution flow.
        
        Args:
            channels: List of channels to distribute to
            name: Name for the flow
        """
        # Default channels if none provided
        target_channels = channels or ["website", "email", "social_media", "blog"]
        
        # Create channel adapter nodes
        channel_nodes = [ChannelAdapterNode(channel=channel) for channel in target_channels]
        
        # Create a distribution coordinator node
        coordinator_node = Node(name="DistributionCoordinator")
        
        # Initialize the flow
        nodes = channel_nodes + [coordinator_node]
        super().__init__(nodes=nodes, name=name)
        
        # Connect all channel nodes to the coordinator
        for node in channel_nodes:
            self.connect(node.name, coordinator_node.name)


class ContentAnalyticsFlow(Flow):
    """
    Flow for content performance analytics.
    
    This flow collects and analyzes performance data, generates insights,
    and provides recommendations for optimization.
    """
    
    def __init__(
        self,
        name: str = "ContentAnalyticsFlow"
    ):
        """
        Initialize a content analytics flow.
        
        Args:
            name: Name for the flow
        """
        # Create analytics nodes for different stages
        data_collection_node = AnalyticsNode(analytics_type="data_collection")
        data_analysis_node = AnalyticsNode(analytics_type="data_analysis")
        insight_generation_node = AnalyticsNode(analytics_type="insight_generation")
        
        # Initialize the flow
        nodes = [data_collection_node, data_analysis_node, insight_generation_node]
        super().__init__(nodes=nodes, name=name)
        
        # Connect nodes sequentially
        for i in range(len(nodes) - 1):
            self.connect(nodes[i].name, nodes[i + 1].name)
