#!/usr/bin/env python3
"""
Debugging example for PocketFlow.
"""
import copy
import time
import inspect
from typing import Dict, Any

from pocketflow_framework import Node, Flow, BaseNode


class DebugFlow(Flow):
    """Debug version of Flow to trace execution."""
    
    def get_next_node(self, curr, action):
        """Debug version of get_next_node."""
        print(f"DEBUG: get_next_node called with action={action}, type={type(action)}")
        print(f"DEBUG: curr.successors={curr.successors}")
        
        # Try to fix the issue by ensuring action is a string
        if isinstance(action, dict):
            print(f"DEBUG: Converting dict action to string 'default'")
            action = "default"
        
        return super().get_next_node(curr, action)


class DebugNode(Node):
    """Debug node implementation."""
    
    def __init__(self, name="node", max_retries=1, wait=0):
        """Initialize the node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data."""
        print(f"[{self.name}] Preparing...")
        return {"name": self.name}
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute node."""
        print(f"[{self.name}] Executing...")
        time.sleep(1)
        result = "default"
        print(f"[{self.name}] exec returning: {result}, type={type(result)}")
        return result
    
    def _run(self, shared):
        """Debug version of _run."""
        print(f"[{self.name}] _run called")
        result = super()._run(shared)
        print(f"[{self.name}] _run returning: {result}, type={type(result)}")
        return result
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Post-process results."""
        print(f"[{self.name}] Post-processing with exec_res={exec_res}, type={type(exec_res)}...")
        shared[f"{self.name}_completed"] = True
        return shared


def main():
    """Run the debugging workflow."""
    print("\n=== PocketFlow Debugging Example ===\n")
    
    # Create nodes
    node1 = DebugNode("research")
    node2 = DebugNode("generation")
    node3 = DebugNode("optimization")
    
    # Connect nodes
    node1.add_successor(node2)
    node2.add_successor(node3)
    
    # Create flow
    flow = DebugFlow(node1)
    
    # Run the workflow
    print("Running workflow...")
    try:
        result = flow.run({})
        print("\nWorkflow completed!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
