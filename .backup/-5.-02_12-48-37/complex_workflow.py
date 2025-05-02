#!/usr/bin/env python3
"""
Complex workflow demonstration using the fixed PocketFlow integration.

This script implements a more complex workflow that combines multiple agents
and tools with branching logic based on execution results.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

# Import agents
from app.agent.react import ReActAgent

# Import tools
from app.tool.bash import Bash
from app.tool.web_search import WebSearch
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.python_execute import PythonExecute

# Import fixed PocketFlow integration
from app.pocketflow.fixed_orchestrator import WorkflowOrchestrator, CustomFlow
from app.pocketflow.fixed_adapters import ToolNode, AgentNode, PocketFlowNode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleReActAgent(ReActAgent):
    """A simple ReAct agent for testing."""

    def __init__(self, name: str = "react_agent"):
        """Initialize a simple ReAct agent."""
        super().__init__(name=name)
        self.system_prompt = f"""
        You are a helpful assistant named {name}.
        """
        self.tools = []

    def add_tool(self, tool):
        """Add a tool to the agent."""
        self.tools.append(tool)

    async def think(self):
        """Think about the next step."""
        # Simple implementation for testing
        return False

    async def act(self):
        """Perform an action."""
        # Simple implementation for testing
        return "Action completed successfully."


class ComplexWorkflow:
    """Implementation of a complex workflow with branching logic."""

    @staticmethod
    async def run_complex_workflow(
        task: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a complex workflow with branching logic based on execution results.

        This workflow includes:
        1. Planning phase with a planning agent
        2. Research phase with a research agent
        3. Code generation with a developer agent
        4. Code validation with a testing tool
        5. Branching based on validation results:
           - If successful, proceed to deployment
           - If failed, go back to code generation with feedback

        Args:
            task: The task to complete
            context: Additional context for the task

        Returns:
            The results from the workflow execution
        """
        # Initialize the orchestrator
        orchestrator = WorkflowOrchestrator()

        # Create agents
        planning_agent = PlanningAgent(name="planner")
        research_agent = SimpleReActAgent(name="researcher")
        developer_agent = SimpleReActAgent(name="developer")
        deployment_agent = SimpleReActAgent(name="deployer")

        # Create tools
        search_tool = WebSearch()
        bash_tool = Bash()
        editor_tool = StrReplaceEditor()
        python_tool = PythonExecute()

        # Add tools to agents
        research_agent.add_tool(search_tool)
        developer_agent.add_tool(editor_tool)
        developer_agent.add_tool(python_tool)
        deployment_agent.add_tool(bash_tool)

        # Register tools and agents
        orchestrator.register_tool(search_tool)
        orchestrator.register_tool(bash_tool)
        orchestrator.register_tool(editor_tool)
        orchestrator.register_tool(python_tool)

        orchestrator.register_agent(planning_agent)
        orchestrator.register_agent(research_agent)
        orchestrator.register_agent(developer_agent)
        orchestrator.register_agent(deployment_agent)

        # Create nodes for each agent and tool
        planner_node = orchestrator.create_agent_node(planning_agent.name, "plan")
        researcher_node = orchestrator.create_agent_node(
            research_agent.name, "research"
        )
        developer_node = orchestrator.create_agent_node(developer_agent.name, "code")
        python_node = orchestrator.create_tool_node(python_tool.name, "validation")
        deployer_node = orchestrator.create_agent_node(
            deployment_agent.name, "deployment"
        )

        # Create a custom validation node that decides the next step based on execution results
        validation_node = PocketFlowNode(name="validation_decision")

        def validation_prep(shared):
            """Prepare data for validation decision."""
            return {
                "validation_result": shared.get("validation", ""),
                "code": shared.get("code", ""),
            }

        def validation_exec(prep_res):
            """Execute validation decision logic."""
            validation_result = prep_res.get("validation_result", "")
            logger.info(f"Making validation decision based on: {validation_result}")

            # Store the decision result
            validation_node.result = {
                "decision": (
                    "success" if "error" not in validation_result.lower() else "failure"
                ),
                "message": validation_result,
            }

            # Return the appropriate action for flow control
            return "success" if "error" not in validation_result.lower() else "failure"

        def validation_post(shared, prep_res, exec_res):
            """Process validation decision results."""
            shared["validation_decision"] = validation_node.result
            return shared

        # Attach methods to the validation node
        validation_node.prep = validation_prep
        validation_node.exec = validation_exec
        validation_node.post = validation_post

        # Create a branching workflow
        nodes = {
            "planner": planner_node,
            "researcher": researcher_node,
            "developer": developer_node,
            "python_execute": python_node,
            "validation": validation_node,
            "deployer": deployer_node,
        }

        # Define the connections between nodes with branching logic
        connections = {
            "planner": {"default": "researcher"},
            "researcher": {"default": "developer"},
            "developer": {"default": "python_execute"},
            "python_execute": {"default": "validation"},
            "validation": {
                "success": "deployer",  # If validation succeeds, go to deployment
                "failure": "developer",  # If validation fails, go back to development
            },
        }

        # Create the workflow
        workflow = orchestrator.create_branching_workflow(
            nodes=nodes,
            connections=connections,
            start_node="planner",
            flow_name="ComplexWorkflow",
        )

        # Run the workflow
        logger.info(f"Running complex workflow with task: {task}")
        result = orchestrator.run_workflow(
            workflow_name="ComplexWorkflow",
            inputs={"task": task, "context": context or {}},
        )

        return result


async def main():
    """Main entry point for the complex workflow runner."""
    # Define a task that requires planning, research, and code execution
    task = "Create a Python script that fetches weather data for a given city using the OpenWeatherMap API"

    # Run the complex workflow
    result = await ComplexWorkflow.run_complex_workflow(task)

    # Display the results
    print("\nComplex Workflow Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
