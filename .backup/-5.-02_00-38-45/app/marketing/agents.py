"""
Marketing-specific agents for PocketFlow integration.

This module provides specialized agents for marketing tasks, including
content planning, creation, optimization, and distribution.
"""

from app.agent.planning import PlanningAgent
from typing import Any, Dict, List, Optional

# Use mock implementation for testing


class ContentPlanningAgent(PlanningAgent):
    """
    Agent specialized in creating and managing content marketing plans.

    This agent helps develop content strategies, editorial calendars,
    and marketing plans based on business goals and target audience.
    """

    def __init__(self, name: str = "content_planning"):
        """Initialize a content planning agent."""
        super().__init__(name=name)

        # Set specialized system prompt for content planning
        self.system_prompt = """
        You are a Content Planning Agent, specialized in developing comprehensive
        content marketing strategies and editorial calendars. Your expertise includes:

        1. Analyzing target audiences and creating detailed personas
        2. Identifying content themes and topics that resonate with the audience
        3. Planning content distribution across multiple channels
        4. Creating editorial calendars with optimal publishing schedules
        5. Aligning content with business goals and marketing objectives

        Help the user develop effective content marketing plans that drive
        engagement, conversions, and brand awareness.
        """


class ContentCreationAgent(PlanningAgent):
    """
    Agent specialized in researching, creating, and optimizing marketing content.

    This agent helps generate high-quality content for various channels,
    ensuring it is engaging, on-brand, and optimized for performance.
    """

    def __init__(self, name: str = "content_creation"):
        """Initialize a content creation agent."""
        super().__init__(name=name)

        # Set specialized system prompt for content creation
        self.system_prompt = """
        You are a Content Creation Agent, specialized in researching, writing,
        and optimizing marketing content. Your expertise includes:

        1. Conducting in-depth research on topics and competitors
        2. Creating engaging and persuasive marketing copy
        3. Optimizing content for SEO and readability
        4. Adapting content for different channels and formats
        5. Ensuring brand voice consistency across all content

        Help the user create high-quality marketing content that resonates
        with their target audience and achieves their marketing objectives.
        """

    async def create_initial_plan(self, request: str) -> Dict[str, Any]:
        """Create an initial content creation plan."""
        # For testing, create a specialized content creation plan
        self.plan = {
            "title": f"Content Creation Plan: {request[:40]}...",
            "content_type": "blog",
            "target_audience": "CMOs and marketing executives",
            "steps": [
                {"id": 1, "description": "Research topic and gather key insights"},
                {"id": 2, "description": "Create content outline with key sections"},
                {
                    "id": 3,
                    "description": "Write first draft focusing on value proposition",
                },
                {"id": 4, "description": "Optimize for SEO and readability"},
                {"id": 5, "description": "Add visuals and formatting for engagement"},
            ],
            "status": "created",
        }
        return self.plan
