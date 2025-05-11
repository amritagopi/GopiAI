"""
Mock implementation of planning agents for testing.

This module provides simplified versions of the planning agents
to allow testing of the marketing automation integration.
"""
from typing import Any, Dict, List, Optional


class PlanningAgent:
    """Mock implementation of PlanningAgent."""

    def __init__(self, name: str = "planning"):
        """Initialize a planning agent."""
        self.name = name
        self.plan = {}

    async def create_initial_plan(self, request: str) -> Dict[str, Any]:
        """Create an initial plan based on the request."""
        # For testing, create a simple mock plan
        self.plan = {
            "title": f"Plan for: {request[:50]}...",
            "steps": [
                {"id": 1, "description": "Research and gather information"},
                {"id": 2, "description": "Create initial draft"},
                {"id": 3, "description": "Review and optimize"},
                {"id": 4, "description": "Finalize and distribute"}
            ],
            "status": "created"
        }
        return self.plan

    async def get_plan(self) -> Dict[str, Any]:
        """Get the current plan."""
        return self.plan

    async def run(self, input_data: dict) -> Dict[str, Any]:
        """Run the planning agent with input data."""
        # Extract the task from input data
        if isinstance(input_data, dict):
            task = input_data.get('task', '')
        else:
            task = str(input_data)

        # Create a plan based on the task
        plan = await self.create_initial_plan(task)
        return plan
