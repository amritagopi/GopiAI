"""
Fixed marketing orchestrator for combining PocketFlow and Manus workflows.

This module extends the WorkflowOrchestrator to provide specialized marketing
automation capabilities, integrating content planning, creation, distribution,
and analytics into cohesive workflows.
"""
from typing import Any, Dict, List, Optional, Union
import copy

from app.pocketflow.orchestrator import WorkflowOrchestrator
from app.agent.base import BaseAgent
from app.flow.base import BaseFlow
from app.tool.base import BaseTool
from pocketflow_framework import Node, Flow, BaseNode

from app.marketing.agents import ContentPlanningAgent
from app.marketing.fixed_nodes import (
    ResearchNode,
    ContentGenerationNode,
    ContentOptimizationNode,
    ChannelAdapterNode,
    AnalyticsNode
)
from app.marketing.tools import (
    ContentResearchTool,
    ContentGenerationTool,
    ContentOptimizationTool,
    ContentDistributionTool,
    ContentAnalyticsTool
)


class CustomFlow(Flow):
    """Custom Flow implementation that returns the shared state."""
    
    def run(self, shared):
        """Override run to return the shared state."""
        # Call the parent's _run method
        self._run(shared)
        # Return the shared state
        return shared


class MarketingOrchestrator(WorkflowOrchestrator):
    """
    Specialized orchestrator for marketing automation workflows.
    
    This class extends the WorkflowOrchestrator to provide marketing-specific
    workflow creation and management capabilities, focusing on content planning,
    creation, distribution, and analytics.
    """
    
    def __init__(self, store: Dict[str, Any] = None):
        """
        Initialize a marketing orchestrator.
        
        Args:
            store: Optional initial shared state for the orchestrator
        """
        super().__init__(store or {})
        
        # Register default marketing tools
        self.register_tool(ContentResearchTool())
        self.register_tool(ContentGenerationTool())
        self.register_tool(ContentOptimizationTool())
        self.register_tool(ContentDistributionTool())
        self.register_tool(ContentAnalyticsTool())
    
    def create_content_planning_workflow(
        self,
        planner_agent: Optional[BaseAgent] = None,
        additional_tools: List[BaseTool] = None,
        flow_name: str = "ContentPlanningWorkflow"
    ) -> BaseFlow:
        """
        Create a workflow for content planning and strategy.
        
        Args:
            planner_agent: Agent responsible for planning (defaults to ContentPlanningAgent)
            additional_tools: Additional tools available for planning
            flow_name: Name for the created flow
            
        Returns:
            A flow that handles content planning and strategy
        """
        # Use default content planning agent if none provided
        if planner_agent is None:
            planner_agent = ContentPlanningAgent()
        
        # Combine default and additional tools
        tools = [
            self.tools.get("content_research_tool", ContentResearchTool()),
            self.tools.get("content_analytics_tool", ContentAnalyticsTool())
        ]
        
        if additional_tools:
            tools.extend(additional_tools)
        
        # Create planning workflow using the parent class method
        return self.create_planning_workflow(
            planner_agent=planner_agent,
            execution_tools=tools,
            flow_name=flow_name
        )
    
    def create_content_creation_workflow(
        self,
        research_node: Optional[Node] = None,
        generation_node: Optional[Node] = None,
        optimization_node: Optional[Node] = None,
        flow_name: str = "ContentCreationWorkflow"
    ) -> CustomFlow:
        """
        Create a workflow for content creation.
        
        Args:
            research_node: Node for content research
            generation_node: Node for content generation
            optimization_node: Node for content optimization
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles content creation
        """
        # Use default nodes if not provided
        research = research_node or ResearchNode()
        generation = generation_node or ContentGenerationNode()
        optimization = optimization_node or ContentOptimizationNode()
        
        # Create a flow starting with the research node
        flow = CustomFlow(research)
        
        # Connect nodes sequentially
        research.add_successor(generation)
        generation.add_successor(optimization)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_content_distribution_workflow(
        self,
        channels: List[str] = None,
        flow_name: str = "ContentDistributionWorkflow"
    ) -> CustomFlow:
        """
        Create a workflow for content distribution across multiple channels.
        
        Args:
            channels: List of channels to distribute content to
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles content distribution
        """
        # Use default channels if none provided
        if channels is None:
            channels = ["website", "email", "social_media"]
        
        # Create channel adapter nodes
        channel_nodes = []
        for channel in channels:
            channel_nodes.append(ChannelAdapterNode(channel=channel))
        
        # Create a flow starting with the first channel node
        if not channel_nodes:
            raise ValueError("No channels specified for distribution workflow")
        
        flow = CustomFlow(channel_nodes[0])
        
        # Connect channel nodes sequentially
        for i in range(len(channel_nodes) - 1):
            channel_nodes[i].add_successor(channel_nodes[i + 1])
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_content_analytics_workflow(
        self,
        flow_name: str = "ContentAnalyticsWorkflow"
    ) -> CustomFlow:
        """
        Create a workflow for content performance analytics.
        
        Args:
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles content analytics
        """
        # Create analytics node
        analytics = AnalyticsNode()
        
        # Create a flow with just the analytics node
        flow = CustomFlow(analytics)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_end_to_end_marketing_workflow(
        self,
        channels: List[str] = None,
        flow_name: str = "EndToEndMarketingWorkflow"
    ) -> CustomFlow:
        """
        Create a comprehensive end-to-end marketing workflow.
        
        This workflow combines planning, creation, distribution, and analytics
        into a single integrated workflow.
        
        Args:
            channels: List of channels to distribute content to
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles the entire marketing process
        """
        # Use default channels if none provided
        if channels is None:
            channels = ["website", "email", "social_media"]
        
        # Create nodes for each stage
        research = ResearchNode()
        generation = ContentGenerationNode()
        optimization = ContentOptimizationNode()
        
        # Create channel adapter nodes
        channel_nodes = []
        for channel in channels:
            channel_nodes.append(ChannelAdapterNode(channel=channel))
        
        analytics = AnalyticsNode()
        
        # Create a flow starting with the research node
        flow = CustomFlow(research)
        
        # Connect nodes sequentially
        research.add_successor(generation)
        generation.add_successor(optimization)
        
        # Connect optimization to the first channel node
        if channel_nodes:
            optimization.add_successor(channel_nodes[0])
            
            # Connect channel nodes sequentially
            for i in range(len(channel_nodes) - 1):
                channel_nodes[i].add_successor(channel_nodes[i + 1])
            
            # Connect the last channel node to analytics
            channel_nodes[-1].add_successor(analytics)
        else:
            # If no channel nodes, connect optimization directly to analytics
            optimization.add_successor(analytics)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def register_pocketflow(self, flow: Flow, name: str) -> None:
        """
        Register a PocketFlow Flow with the orchestrator.
        
        Args:
            flow: The PocketFlow Flow to register
            name: Name to register the flow under
        """
        self.flows[name] = flow
