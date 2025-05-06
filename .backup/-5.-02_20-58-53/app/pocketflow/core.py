"""
Core PocketFlow classes and interfaces.

This module provides the core classes and interfaces for PocketFlow integration,
with implementations that work whether or not the actual PocketFlow library is available.
"""
from typing import Any, Dict, List, Optional, Union, Callable
import os
import sys
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Try to import from the actual PocketFlow library
POCKETFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'PocketFlow')
sys.path.append(POCKETFLOW_DIR)

try:
    # Try to import from the actual PocketFlow library
    from pocketflow_framework import Node as PFNode
    from pocketflow_framework import Flow as PFFlow
    from pocketflow_framework import BatchNode as PFBatchNode
    
    logger.info("Using actual PocketFlow implementation")
    class Node(PFNode):
        """Wrapper around PocketFlow's Node class."""
        
        def __init__(self, *args, **kwargs):
            # Extract name if provided as a keyword argument
            name = kwargs.pop('name', None) if 'name' in kwargs else None
            
            # Initialize with proper parameters for pocketflow_framework
            # The Node class in pocketflow_framework expects max_retries and wait as parameters
            max_retries = kwargs.pop('max_retries', 1) if 'max_retries' in kwargs else 1
            wait = kwargs.pop('wait', 0) if 'wait' in kwargs else 0
            
            # Initialize the parent class with the correct parameters
            super().__init__(max_retries=max_retries, wait=wait)
            
            # Set name if provided
            if name:
                self.name = name
        
    class Flow(PFFlow):
        """Wrapper around PocketFlow's Flow class."""
        
        def __init__(self, *args, **kwargs):
            # Extract nodes and name from kwargs if they exist
            nodes = kwargs.pop('nodes', []) if 'nodes' in kwargs else []
            name = kwargs.pop('name', None) if 'name' in kwargs else None
            
            # Ensure we have a start node if required by pocketflow_framework
            # If nodes are provided, use the first one as the start node
            if not args and nodes:
                start_node = nodes[0]
                super().__init__(start_node, **kwargs)
            else:
                # If no nodes or args are provided, this will raise an error
                # which is the expected behavior
                super().__init__(*args, **kwargs)
            
            # Add remaining nodes to the flow if provided
            if nodes and len(nodes) > 1:
                # Connect nodes sequentially
                for i in range(len(nodes) - 1):
                    nodes[i].add_successor(nodes[i + 1])
                
            # Set name if provided
            if name:
                self.name = name
        
        def connect(self, source_name, target_name):
            """Connect nodes by their names."""
            # This is a simplified implementation that assumes nodes are already added
            # In a real implementation, we would need to find the nodes by name
            # and then connect them using add_successor
            pass
        
    class BatchNode(PFBatchNode):
        """Wrapper around PocketFlow's BatchNode class."""
        pass
        
except ImportError:
    # Provide fallback implementations if PocketFlow is not available
    class Node:
        """
        A node in a workflow that processes data.
        
        This is a fallback implementation for when PocketFlow is not available.
        """
        def __init__(self, name: Optional[str] = None):
            """Initialize a Node.
            
            Args:
                name: Optional name for the node
            """
            self.name = name or self.__class__.__name__
            
        def prep(self, store: Dict[str, Any]) -> Dict[str, Any]:
            """Extract relevant data from store for execution.
            
            Args:
                store: The shared data store
                
            Returns:
                A dictionary of data to be passed to exec
            """
            return {}
            
        def exec(self, data: Dict[str, Any]) -> Any:
            """Execute the node's logic with the provided data.
            
            Args:
                data: The data to process
                
            Returns:
                The result of the execution
            """
            return None
            
        def post(self, result: Any, store: Dict[str, Any]) -> Dict[str, Any]:
            """Process the result and update the shared store.
            
            Args:
                result: The result from exec
                store: The shared data store
                
            Returns:
                The updated store
            """
            return store
    
    class Flow:
        """
        A workflow that connects and executes nodes.
        
        This is a fallback implementation for when PocketFlow is not available.
        """
        def __init__(self, nodes: Optional[List[Node]] = None, name: Optional[str] = None):
            """Initialize a Flow.
            
            Args:
                nodes: Optional list of nodes in the flow
                name: Optional name for the flow
            """
            self.nodes = nodes or []
            self.name = name or 'DefaultFlow'
            self.connections = {}
        
        def connect(self, source: Union[str, Node], target: Union[str, Node]) -> None:
            """Connect two nodes in the flow.
            
            Args:
                source: The source node or node name
                target: The target node or node name
            """
            source_name = source if isinstance(source, str) else source.name
            target_name = target if isinstance(target, str) else target.name
            
            if source_name not in self.connections:
                self.connections[source_name] = []
                
            self.connections[source_name].append(target_name)
            
        def run(self, store: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            """Run the flow with the provided store.
            
            Args:
                store: Optional initial data store
                
            Returns:
                The final data store after execution
            """
            # In the mock implementation, just return the store unchanged
            return store or {}
            
    class BatchNode(Node):
        """
        A node that processes multiple items in parallel.
        
        This is a fallback implementation for when PocketFlow is not available.
        """
        def __init__(self, name: Optional[str] = None):
            """Initialize a BatchNode.
            
            Args:
                name: Optional name for the node
            """
            super().__init__(name=name)
