"""
Marketing-specific nodes for PocketFlow integration.

This module provides specialized nodes for marketing tasks that can be used
in PocketFlow workflows, focusing on research, content generation, optimization,
channel adaptation, and analytics.
"""
from typing import Any, Dict, List, Optional
import json

from pocketflow_framework import Node

from app.marketing.tools import (
    ContentResearchTool,
    ContentGenerationTool,
    ContentOptimizationTool,
    ContentDistributionTool,
    ContentAnalyticsTool
)


class ResearchNode(Node):
    """Node for content research."""
    
    def __init__(self, max_retries: int = 3, wait: int = 1):
        """Initialize with a content research tool."""
        super().__init__(max_retries=max_retries, wait=wait)
        from app.marketing.tools import ContentResearchTool
        self.research_tool = ContentResearchTool()
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for research."""
        # Extract topic and research parameters
        data = {
            "topic": shared.get("topic", "marketing automation"),
            "research_type": shared.get("research_type", "keyword"),
            "depth": shared.get("depth", "detailed")
        }
        
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute research."""
        self.result = self.research_tool.execute(**prep_res)
        # Return "default" to use the default successor
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process research results and update the store."""
        # Update the store with research results
        shared["research_results"] = self.result
        shared["research_keywords"] = self.result.get("keywords", [])
        shared["research_sources"] = self.result.get("sources", [])
        shared["research_trends"] = self.result.get("trends", [])
        shared["research_completed"] = True
        
        return shared


class ContentGenerationNode(Node):
    """Node for generating marketing content."""
    
    def __init__(self, max_retries: int = 3, wait: int = 1):
        """Initialize with a content generation tool."""
        super().__init__(max_retries=max_retries, wait=wait)
        from app.marketing.tools import ContentGenerationTool
        self.generation_tool = ContentGenerationTool()
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for content generation."""
        # Get research results from shared state
        research_results = shared.get("research_results", {})
        
        # Prepare data for content generation
        data = {
            "content_type": shared.get("content_type", "blog"),
            "topic": shared.get("topic", "marketing automation"),
            "target_audience": shared.get("target_audience", "marketing professionals"),
            "tone": shared.get("tone", "professional"),
            "length": shared.get("length", "medium"),
            "keywords": research_results.get("keywords", [])
        }
        
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute content generation."""
        self.result = self.generation_tool.execute(**prep_res)
        # Return "default" to use the default successor
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process generation results and update the store."""
        # Update the store with generation results
        shared["generated_content"] = self.result.get("generated_content", "")
        shared["content_type"] = self.result.get("content_type", shared.get("content_type", ""))
        shared["generation_completed"] = True
        
        return shared


class ContentOptimizationNode(Node):
    """Node for optimizing marketing content."""
    
    def __init__(self, optimization_type: str = "all", max_retries: int = 3, wait: int = 1):
        """Initialize with a content optimization tool."""
        super().__init__(max_retries=max_retries, wait=wait)
        from app.marketing.tools import ContentOptimizationTool
        self.optimization_tool = ContentOptimizationTool()
        self.optimization_type = optimization_type
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for content optimization."""
        # Get generated content from shared state
        content = shared.get("generated_content", "")
        
        # Get research keywords if available
        keywords = shared.get("research_keywords", [])
        
        # Prepare data for optimization
        data = {
            "content": content,
            "optimization_type": shared.get("optimization_type", self.optimization_type),
            "target_keywords": keywords
        }
        
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute content optimization."""
        self.result = self.optimization_tool.execute(**prep_res)
        # Return "default" to use the default successor
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process optimization results and update the store."""
        # Update the store with optimization results
        shared["optimized_content"] = self.result.get("optimized_content", shared.get("generated_content", ""))
        shared["optimization_recommendations"] = self.result.get("recommendations", [])
        shared["optimization_completed"] = True
        
        return shared


class ChannelAdapterNode(Node):
    """Node for adapting content to specific marketing channels."""
    
    def __init__(self, channel: str = "website", max_retries: int = 3, wait: int = 1):
        """Initialize with a channel adapter tool."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.channel = channel
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for channel adaptation."""
        # Get optimized content from shared state
        content = shared.get("optimized_content", shared.get("generated_content", ""))
        
        # Prepare data for adaptation
        data = {
            "content": content,
            "channel": self.channel,
            "target_audience": shared.get("target_audience", "general")
        }
        
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute channel adaptation."""
        # For testing, just create a simple adaptation
        content = prep_res.get("content", "")
        adapted_content = f"Adapted for {self.channel}: {content[:100]}..."
        
        self.result = {
            "channel": self.channel,
            "adapted_content": adapted_content,
            "original_content": content
        }
        
        # Return "default" to use the default successor
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process adaptation results and update the store."""
        # Update the store with adaptation results
        if "channel_adaptations" not in shared:
            shared["channel_adaptations"] = {}
        
        shared["channel_adaptations"][self.channel] = self.result.get("adapted_content", "")
        shared["adaptation_completed"] = True
        
        return shared


class AnalyticsNode(Node):
    """Node for analyzing marketing content performance."""
    
    def __init__(self, analytics_type: str = "data_collection", max_retries: int = 3, wait: int = 1):
        """Initialize with an analytics tool."""
        super().__init__(max_retries=max_retries, wait=wait)
        from app.marketing.tools import ContentAnalyticsTool
        self.analytics_tool = ContentAnalyticsTool()
        self.analytics_type = analytics_type
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for analytics."""
        # Get channel adaptations from shared state
        channels = list(shared.get("channel_adaptations", {}).keys())
        
        # Prepare data for analytics
        data = {
            "content_id": shared.get("content_id", "current"),
            "channels": channels,
            "metrics": shared.get("metrics", ["views", "engagement", "conversion"]),
            "time_period": shared.get("time_period", "last_week")
        }
        
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute analytics."""
        self.result = self.analytics_tool.execute(**prep_res)
        # Return "default" to use the default successor
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process analytics results and update the store."""
        # Update the store with analytics results
        shared["analytics_results"] = self.result
        shared["analytics_insights"] = self.result.get("insights", [])
        shared["analytics_completed"] = True
        
        return shared
