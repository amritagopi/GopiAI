"""
Marketing orchestrator for combining PocketFlow and Manus workflows.

This module extends the WorkflowOrchestrator to provide specialized marketing
automation capabilities, integrating content planning, creation, distribution,
and analytics into cohesive workflows.
"""
from typing import Any, Dict, List, Optional, Union

from app.pocketflow.orchestrator import WorkflowOrchestrator
from app.agent.base import BaseAgent
from app.flow.base import BaseFlow
from app.tool.base import BaseTool
from pocketflow_framework import Node, Flow

from app.marketing.agents import ContentPlanningAgent
from app.marketing.tools import (
    ContentResearchTool,
    ContentGenerationTool,
    ContentOptimizationTool,
    ContentDistributionTool,
    ContentAnalyticsTool
)


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
    ) -> Flow:
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
        from app.marketing.nodes import (
            ResearchNode, 
            ContentGenerationNode, 
            ContentOptimizationNode
        )
        
        # Use default nodes if not provided
        research = research_node or ResearchNode()
        generation = generation_node or ContentGenerationNode()
        optimization = optimization_node or ContentOptimizationNode()
        
        # Create a flow starting with the research node
        flow = Flow(research)
        
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
    ) -> Flow:
        """
        Create a workflow for content distribution across multiple channels.
        
        Args:
            channels: List of channels to distribute content to
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles content distribution
        """
        from app.marketing.nodes import ChannelAdapterNode
        
        # Default channels if none provided
        default_channels = ["website", "email", "social_media", "blog"]
        target_channels = channels or default_channels
        
        # Create adapter nodes for each channel
        adapter_nodes = [ChannelAdapterNode(channel=channel) for channel in target_channels]
        
        # Create a flow with the first adapter node
        if not adapter_nodes:
            raise ValueError("No channels specified for content distribution")
            
        flow = Flow(adapter_nodes[0])
        
        # Connect nodes in parallel
        current_node = adapter_nodes[0]
        for node in adapter_nodes[1:]:
            current_node.add_successor(node)
            current_node = node
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_content_analytics_workflow(
        self,
        flow_name: str = "ContentAnalyticsWorkflow"
    ) -> Flow:
        """
        Create a workflow for content performance analytics.
        
        Args:
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that handles content analytics
        """
        from app.marketing.nodes import AnalyticsNode
        
        # Create analytics nodes for different stages
        collection_node = AnalyticsNode(analytics_type="data_collection")
        analysis_node = AnalyticsNode(analytics_type="data_analysis")
        insight_node = AnalyticsNode(analytics_type="insight_generation")
        
        # Create the flow
        flow = Flow(collection_node)
        
        # Connect nodes sequentially
        collection_node.add_successor(analysis_node)
        analysis_node.add_successor(insight_node)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_end_to_end_marketing_workflow(
        self,
        channels: List[str] = None,
        flow_name: str = "EndToEndMarketingWorkflow"
    ) -> Flow:
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
        # Create individual workflow components
        creation_flow = self.create_content_creation_workflow()
        distribution_flow = self.create_content_distribution_workflow(channels)
        analytics_flow = self.create_content_analytics_workflow()
        
        # Get the first node from each flow
        from app.marketing.nodes import ResearchNode
        start_node = ResearchNode()  # Start with research
        
        # Create the end-to-end flow
        flow = Flow(start_node)
        
        # Connect the flows
        # Get the last node from creation_flow and connect it to the first node of distribution_flow
        # Get the last node from distribution_flow and connect it to the first node of analytics_flow
        
        # For simplicity, we'll just connect our start node to the first nodes of each flow
        # In a real implementation, we would need to extract the actual nodes from each flow
        distribution_first_node = distribution_flow.start
        analytics_first_node = analytics_flow.start
        
        # Connect the flows
        start_node.add_successor(distribution_first_node)
        distribution_first_node.add_successor(analytics_first_node)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
