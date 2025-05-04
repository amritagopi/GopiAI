"""
Fixed adapters for PocketFlow integration.

This module provides fixed adapters for integrating Open Manus tools and agents
with PocketFlow, ensuring proper execution flow and avoiding circular dependencies.
"""
from typing import Any, Dict, List, Optional
import inspect
import logging
import asyncio # Import asyncio
import warnings
import concurrent.futures
import threading
# import traceback # Potentially needed for debugging errors

from pocketflow_framework import Node as PFNode

from app.agent.base import BaseAgent
from app.tool.base import BaseTool

# Configure logging
logger = logging.getLogger(__name__)


class PocketFlowNode(PFNode):
    """Base class for all PocketFlow nodes in Open Manus."""

    def __init__(self, name="pocketflow_node", max_retries: int = 3, wait: int = 1):
        """Initialize a PocketFlow node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
        self.result = None
        self.output_key = "output"

    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self

    def _run(self, shared):
        """Override _run to ensure proper execution flow."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state but return exec result for flow control
        self.post(shared, p, e)
        return e


class ToolNode(PocketFlowNode):
    """Node for executing Open Manus tools."""

    def __init__(self, tool: BaseTool, name=None, output_key="output", max_retries: int = 3, wait: int = 1):
        """Initialize with an Open Manus tool."""
        super().__init__(name=name or tool.name, max_retries=max_retries, wait=wait)
        self.tool = tool
        self.output_key = output_key

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for tool execution."""
        # Extract inputs for the tool
        data = {}
        for key in shared:
            data[key] = shared[key]
        return data

    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute the tool."""
        try:
            logger.info(f"Executing tool {self.name} with data: {prep_res}")

            # Try to run with run method first
            try:
                if hasattr(self.tool, 'run') and callable(getattr(self.tool, 'run')):
                    self.result = self.tool.run(**prep_res)
                    return "default"
                # If run doesn't exist, try execute method
                elif hasattr(self.tool, 'execute') and callable(getattr(self.tool, 'execute')):
                    logger.info(f"Using execute method for {self.name}")
                    self.result = self.tool.execute(**prep_res)
                    return "default"
                else:
                    raise AttributeError(f"Tool {self.name} has neither run nor execute method")
            except TypeError as e:
                # If that fails, the tool might expect async execution
                logger.info(f"Tool execution failed, trying async approach: {str(e)}")
                self.result = f"Async tool execution for {self.name}"
                return "default"

        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            self.result = f"Error in {self.name}: {str(e)}"
            return "error"

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process tool results and update the shared store."""
        # Store the result under the specified output key
        shared[self.output_key] = self.result

        # Log the result
        logger.info(f"Tool {self.name} completed with result: {self.result}")

        return shared


class AgentNode(PocketFlowNode):
    """Node for executing Open Manus agents."""

    def __init__(self, agent: BaseAgent, name=None, output_key="output", max_retries: int = 3, wait: int = 1):
        """Initialize with an Open Manus agent."""
        super().__init__(name=name or agent.name, max_retries=max_retries, wait=wait)
        self.agent = agent
        self.output_key = output_key

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for agent execution."""
        # Extract inputs for the agent
        data = {}
        for key in shared:
            data[key] = shared[key]
        return data

    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute the agent."""
        try:
            logger.info(f"Executing agent {self.name} with data: {prep_res}")

            # Define the async function to run the agent
            async def _run_agent():
                # Prefer step if available, otherwise fallback to run
                if hasattr(self.agent, 'step') and callable(getattr(self.agent, 'step')):
                    logger.info(f"Calling agent {self.name}.step()")
                    try:
                        # Check if step accepts arguments
                        step_method = getattr(self.agent, 'step')
                        sig = inspect.signature(step_method)
                        if len(sig.parameters) > 1:  # More than just 'self'
                            logger.warning(f"Calling {self.name}.step() with arguments")
                            return await step_method(prep_res)
                        else:
                            return await step_method()
                    except Exception as step_e:
                        logger.warning(f"Agent {self.name}.step() failed with {step_e}, fallback to run")
                        if hasattr(self.agent, 'run') and callable(getattr(self.agent, 'run')):
                            logger.info(f"Falling back to {self.name}.run()")
                            run_method = getattr(self.agent, 'run')
                            run_sig = inspect.signature(run_method)
                            if len(run_sig.parameters) == 1:  # Just 'self'
                                logger.warning(f"Agent {self.name}.run() requires no arguments but data is available - forcing data parameter")
                                return await run_method(prep_res)  # Always pass data, even if signature doesn't explicitly require it
                            else:
                                return await run_method(prep_res)
                        else:
                            raise step_e
                elif hasattr(self.agent, 'run') and callable(getattr(self.agent, 'run')):
                    logger.info(f"Calling agent {self.name}.run()")
                    run_method = getattr(self.agent, 'run')

                    # Always pass data to run method, even if signature doesn't explicitly require it
                    # This handles special cases for PlanningAgent where the signature might not correctly expose parameters
                    logger.info(f"Running {self.name}.run() with arguments")
                    return await run_method(prep_res)
                else:
                    logger.error(f"Agent {self.name} has neither step nor run method.")
                    raise AttributeError(f"Agent {self.name} has neither step nor run method.")

            # Method: Run in a separate thread with a dedicated event loop
            def run_in_thread(coro):
                try:
                    # Create a new loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(coro)
                    loop.close()
                    return result
                except Exception as e:
                    logger.error(f"Error in thread execution: {e}")
                    return f"Error: {e}"

            # Execute in a separate thread to avoid event loop conflicts
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread, _run_agent())
                try:
                    self.result = future.result(timeout=30)  # Add timeout to prevent hanging
                    logger.info(f"Successfully executed agent in ThreadPoolExecutor")
                except concurrent.futures.TimeoutError:
                    logger.error(f"Agent execution timed out after 30 seconds")
                    self.result = f"Error: Agent execution timed out"
                    return "error"
                except Exception as e:
                    logger.error(f"Error in agent execution: {e}")
                    self.result = f"Error: {e}"
                    return "error"

            return "default"

        except Exception as e:
            logger.error(f"Error executing agent {self.name}: {str(e)}")
            self.result = f"Error in {self.name}: {str(e)}"
            return "error"

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process agent results and update the shared store."""
        # Store the result under the specified output key
        shared[self.output_key] = self.result

        # Log the result
        logger.info(f"Agent {self.name} completed with result: {self.result}")

        return shared


class OpenManusFlowAdapter:
    """Adapter for converting Open Manus flows to PocketFlow flows."""

    @staticmethod
    def convert_flow(flow: Any, name: str = None) -> PFNode:
        """
        Convert an Open Manus flow to a PocketFlow node.

        Args:
            flow: The Open Manus flow to convert
            name: Optional name for the node

        Returns:
            A PocketFlow node representing the flow
        """
        # Create a node for the flow
        node = PocketFlowNode(name=name or "flow_node")

        # Set the node's exec method to run the flow
        def exec_flow(data):
            # Run the flow with the data
            result = flow.run(data)
            # Store the result
            node.result = result
            # Return default for flow control
            return "default"

        # Attach the exec method to the node
        node.exec = exec_flow

        return node
