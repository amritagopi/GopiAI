#!/usr/bin/env python3
"""
Example based on PocketFlow documentation.
"""
import time
from typing import Any, Dict

from pocketflow_framework import Flow, Node


class SimpleNode(Node):
    """Simple node implementation."""
    
    def __init__(self, name="node", max_retries=1, wait=0):
        """Initialize the node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
        self.result = None
    
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
        print(f"[{self.name}] Executing with {prep_res}...")
        time.sleep(1)
        self.result = f"{self.name} result"
        return "default"  # This is the key to look up in successors
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Post-process results."""
        print(f"[{self.name}] Post-processing with exec_res={exec_res}...")
        shared[f"{self.name}_result"] = self.result
        shared[f"{self.name}_completed"] = True
        return shared
        
    def _run(self, shared):
        """Override _run to ensure proper handling of return values."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state
        self.post(shared, p, e)
        # Return the key for the next node, not the result
        return e


def main():
    """Run the example workflow."""
    print("\n=== PocketFlow Documentation Example ===\n")
    
    # Create nodes
    node1 = SimpleNode("research")
    node2 = SimpleNode("generation")
    node3 = SimpleNode("optimization")
    
    # Connect nodes
    node1.add_successor(node2)
    node2.add_successor(node3)
    
    # Create flow
    flow = Flow(node1)
    
    # Run the workflow
    print("Running workflow...")
    shared_state = {}
    result = flow.run(shared_state)
    
    print("\nWorkflow completed!")
    print(f"Shared state: {shared_state}")


if __name__ == "__main__":
    main()
