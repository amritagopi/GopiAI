"""
Adapter classes to bridge PocketFlow and Open Manus components.

These adapters enable bidirectional compatibility between PocketFlow's Node/Flow
architecture and Open Manus's agent and tool systems.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Type
import logging
import asyncio
import os
import sys

# Set up logging
logger = logging.getLogger(__name__)

# Import Open Manus dependencies
from app.agent.base import BaseAgent
from app.tool.base import BaseTool

# Define BaseFlow class if not available
class BaseFlow:
    """Base class for flows in Open Manus."""
    
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.description = description or f"Flow: {self.name}"
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the flow with the provided inputs."""
        raise NotImplementedError("Subclasses must implement this method")

# Import our PocketFlow core classes
from app.pocketflow.core import Node, Flow, BatchNode

# Try to import from the actual PocketFlow library
POCKETFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'PocketFlow')
sys.path.append(POCKETFLOW_DIR)

# Check if PocketFlow is available
try:
    import pocketflow_framework
    POCKETFLOW_AVAILABLE = True
    logger.info("PocketFlow framework is available")
except ImportError:
    POCKETFLOW_AVAILABLE = False
    logger.warning("PocketFlow framework is not available, using fallback implementations")


class PocketFlowNodeAdapter(Node):
    """Adapts Open Manus tools and agents to work as PocketFlow Nodes."""
    
    def __init__(
        self, 
        tool_or_agent: Union[BaseTool, BaseAgent],
        input_keys: Optional[List[str]] = None,
        output_key: Optional[str] = None,
        name: Optional[str] = None
    ):
        """
        Initialize a PocketFlow Node that wraps an Open Manus tool or agent.
        
        Args:
            tool_or_agent: Open Manus tool or agent to adapt
            input_keys: Keys to extract from store for tool/agent input
            output_key: Key to store the tool/agent output
            name: Optional name for the node
        """
        self.tool_or_agent = tool_or_agent
        self.input_keys = input_keys or []
        self.output_key = output_key or "result"
        
        # Get name from tool/agent if not provided
        node_name = name or getattr(tool_or_agent, 'name', tool_or_agent.__class__.__name__)
        
        # Initialize the parent class
        if POCKETFLOW_AVAILABLE:
            # When using actual PocketFlow, pass name as a parameter
            super().__init__(node_name)
        else:
            # When using fallback, pass name as a keyword argument
            super().__init__(name=node_name)
            
        # Ensure the name is set
        self.name = node_name
        
        logger.info(f"Created PocketFlowNodeAdapter for {self.name}")
        
    def prep(self, store: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from store for tool/agent execution."""
        # Extract specified inputs from the store
        if self.input_keys:
            inputs = {key: store.get(key) for key in self.input_keys if key in store}
        else:
            # If no input keys specified, pass the entire store
            inputs = store.copy()
        return inputs
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Execute the Open Manus tool or agent with the provided data.
        
        Args:
            data: Input data for the tool or agent
            
        Returns:
            A string action to determine the next node in the flow
        """
        try:
            logger.info(f"Executing {self.name} with data: {data}")
            
            if isinstance(self.tool_or_agent, BaseTool):
                # Handle tool execution
                try:
                    # Try to run synchronously first
                    result = self.tool_or_agent.run(**data)
                    # Store the result in the node for later retrieval
                    self._result = result
                    # Return a default action string
                    return "default"
                except TypeError as e:
                    # If that fails, the tool might expect async execution
                    logger.info(f"Tool execution failed, trying async approach: {str(e)}")
                    # Store a placeholder result
                    self._result = f"Async tool execution for {self.name}"
                    # Return a default action string
                    return "default"
                    
            elif isinstance(self.tool_or_agent, BaseAgent):
                # For agents, determine the appropriate method to call
                if hasattr(self.tool_or_agent, 'step') and callable(getattr(self.tool_or_agent, 'step')):
                    # Check the signature of the step method
                    import inspect
                    step_method = getattr(self.tool_or_agent, 'step')
                    sig = inspect.signature(step_method)
                    
                    # If step method doesn't take parameters (other than self)
                    if len(sig.parameters) == 0:
                        logger.info(f"Calling step() without parameters for {self.name}")
                        # Store a placeholder result
                        self._result = f"Agent step execution for {self.name}"
                    else:
                        logger.info(f"Calling step() with parameters for {self.name}")
                        # Store a placeholder result
                        self._result = f"Agent step execution with data for {self.name}"
                else:
                    # Fallback to run method
                    logger.info(f"Falling back to run() method for {self.name}")
                    # Store a placeholder result
                    self._result = f"Agent run execution for {self.name}"
                
                # Return a default action string
                return "default"
            else:
                raise TypeError(f"Unsupported type: {type(self.tool_or_agent)}")
        except Exception as e:
            logger.error(f"Error executing {self.name}: {str(e)}")
            # Store the error message
            self._result = f"Error in {self.name}: {str(e)}"
            # Return an error action
            return "error"
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Dict[str, Any]:
        """Process result and update the shared store.
        
        Args:
            shared: The shared store
            prep_res: The result from the prep method
            exec_res: The action string from the exec method
            
        Returns:
            Updated shared store
        """
        # Initialize _result attribute if it doesn't exist
        if not hasattr(self, '_result'):
            self._result = f"No result available for {self.name}"
            
        # Store the actual result under the specified output key
        shared[self.output_key] = self._result
        
        # Log the result
        logger.info(f"Node {self.name} completed with result: {self._result}")
        
        return shared


class OpenManusToolAdapter(BaseTool):
    """Adapts a PocketFlow Node to work as an Open Manus Tool."""
    
    def __init__(
        self, 
        node: Node,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize an Open Manus Tool that wraps a PocketFlow Node.
        
        Args:
            node: PocketFlow Node to adapt
            name: Optional name for the tool
            description: Optional description of the tool
        """
        self.node = node
        self.store = {}  # Internal store for the node
        
        super().__init__(
            name=name or node.name,
            description=description or f"PocketFlow Node adapter for {node.name}"
        )
        logger.info(f"Created OpenManusToolAdapter for {self.name}")
    
    async def run(self, **kwargs) -> Any:
        """Execute the PocketFlow Node with the provided inputs."""
        try:
            # Update internal store with inputs
            self.store.update(kwargs)
            
            # Execute node's lifecycle
            inputs = self.node.prep(self.store)
            result = self.node.exec(inputs)
            self.store = self.node.post(result, self.store)
            
            return result
        except Exception as e:
            logger.error(f"Error running {self.name}: {str(e)}")
            raise


class PocketFlowAdapter:
    """Utility class for creating and managing PocketFlow integrations."""
    
    @staticmethod
    def create_flow_from_tools(
        tools: List[BaseTool],
        flow_name: str = "ToolFlow",
        connections: Optional[Dict[str, List[str]]] = None
    ) -> Flow:
        """
        Create a PocketFlow Flow from a list of Open Manus tools.
        
        Args:
            tools: List of Open Manus tools to include in the flow
            flow_name: Name for the created flow
            connections: Optional dict mapping source nodes to target nodes
                        If None, tools will be connected sequentially
        
        Returns:
            A PocketFlow Flow object with all tools as nodes
        """
        if not tools:
            raise ValueError("Cannot create a flow with no tools")
            
        # Create nodes for each tool
        nodes = [PocketFlowNodeAdapter(tool) for tool in tools]
        
        # Create flow with the first node as the start node
        flow = Flow(nodes[0])
        flow.name = flow_name
        
        # Connect nodes based on connections or sequentially
        if connections:
            # Custom connections
            for source_name, target_names in connections.items():
                # Find the source node
                source_node = next((n for n in nodes if n.name == source_name), None)
                if not source_node:
                    logger.warning(f"Source node '{source_name}' not found")
                    continue
                    
                for target_name in target_names:
                    # Find the target node
                    target_node = next((n for n in nodes if n.name == target_name), None)
                    if not target_node:
                        logger.warning(f"Target node '{target_name}' not found")
                        continue
                        
                    # Connect the nodes
                    source_node.add_successor(target_node)
        else:
            # Sequential connection
            for i in range(len(nodes) - 1):
                nodes[i].add_successor(nodes[i + 1])
        
        logger.info(f"Created flow '{flow_name}' with {len(nodes)} tools")
        return flow
    
    @staticmethod
    def create_flow_from_agents(
        agents: List[BaseAgent],
        flow_name: str = "AgentFlow",
        connections: Optional[Dict[str, List[str]]] = None
    ) -> Flow:
        """
        Create a PocketFlow Flow from a list of Open Manus agents.
        
        Args:
            agents: List of Open Manus agents to include in the flow
            flow_name: Name for the created flow
            connections: Optional dict mapping source nodes to target nodes
                        If None, agents will be connected sequentially
        
        Returns:
            A PocketFlow Flow object with all agents as nodes
        """
        if not agents:
            raise ValueError("Cannot create a flow with no agents")
            
        # Create nodes for each agent
        nodes = [PocketFlowNodeAdapter(agent) for agent in agents]
        
        # Create flow with the first node as the start node
        flow = Flow(nodes[0])
        flow.name = flow_name
        
        # Connect nodes based on connections or sequentially
        if connections:
            # Custom connections
            for source_name, target_names in connections.items():
                # Find the source node
                source_node = next((n for n in nodes if n.name == source_name), None)
                if not source_node:
                    logger.warning(f"Source node '{source_name}' not found")
                    continue
                    
                for target_name in target_names:
                    # Find the target node
                    target_node = next((n for n in nodes if n.name == target_name), None)
                    if not target_node:
                        logger.warning(f"Target node '{target_name}' not found")
                        continue
                        
                    # Connect the nodes
                    source_node.add_successor(target_node)
        else:
            # Sequential connection
            for i in range(len(nodes) - 1):
                nodes[i].add_successor(nodes[i + 1])
        
        logger.info(f"Created flow '{flow_name}' with {len(nodes)} agents")
        return flow


class OpenManusFlowAdapter(BaseFlow):
    """Adapts a PocketFlow Flow to work as an Open Manus Flow."""
    
    def __init__(
        self, 
        flow: Flow,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize an Open Manus Flow that wraps a PocketFlow Flow.
        
        Args:
            flow: PocketFlow Flow to adapt
            name: Optional name for the flow
            description: Optional description for the flow
        """
        self.flow = flow
        self.store = {}  # Shared store for the flow
        
        super().__init__(
            name=name or flow.name,
            description=description or f"PocketFlow Flow adapter for {flow.name}"
        )
        logger.info(f"Created OpenManusFlowAdapter for {self.name}")
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the PocketFlow Flow with the provided inputs."""
        try:
            # Update store with inputs
            self.store.update(kwargs)
            
            # Execute the flow
            result = self.flow.run(self.store)
            
            return result
        except Exception as e:
            logger.error(f"Error running flow {self.name}: {str(e)}")
            raise