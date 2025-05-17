#!/usr/bin/env python3
"""
Simple example of using PocketFlow for marketing workflows.

This example demonstrates how to create a basic marketing workflow
using the PocketFlow framework with research, content generation,
and optimization steps.
"""
import time
from typing import Any, Dict

from pocketflow_framework import BaseNode, Flow, Node


class SimpleResearchNode(Node):
    """Node for simple content research."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the research node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.successors = {}  # Dictionary to store successor nodes
        self.result = None
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for research."""
        print(f"Researching topic: {shared.get('topic', 'general topic')}")
        return {"topic": shared.get("topic", "general topic")}
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute research."""
        # Simulate research work
        time.sleep(1)
        
        # Store results for post-processing
        self.result = {
            "keywords": ["ai", "automation", "marketing", "efficiency"],
            "sources": ["industry reports", "competitor analysis"],
            "trends": ["personalization", "automation"]
        }
        
        # Return the key for the next node to execute
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process research results and update the shared state."""
        # Update the shared state with research results
        shared["research_results"] = self.result
        shared["research_completed"] = True
        print(f"Research completed. Found keywords: {self.result['keywords']}")
        return shared
        
    def _run(self, shared):
        """Override _run to ensure proper handling of return values."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state
        self.post(shared, p, e)
        # Return the key for the next node, not the result
        return e


class SimpleContentGenerationNode(Node):
    """Node for simple content generation."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the content generation node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.successors = {}
        self.result = None
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for content generation."""
        research_results = shared.get("research_results", {})
        return {
            "topic": shared.get("topic", "general topic"),
            "keywords": research_results.get("keywords", []),
            "content_type": shared.get("content_type", "blog")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute content generation."""
        # Simulate content generation
        time.sleep(1)
        
        topic = prep_res.get("topic", "general topic")
        keywords = ", ".join(prep_res.get("keywords", []))
        
        # Store results for post-processing
        self.result = {
            "content": f"Generated content about {topic} using keywords: {keywords}",
            "content_type": prep_res.get("content_type", "blog")
        }
        
        # Return the key for the next node to execute
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process generation results and update the shared state."""
        # Update the shared state with generation results
        shared["generated_content"] = self.result["content"]
        shared["content_type"] = self.result["content_type"]
        shared["generation_completed"] = True
        print(f"Content generation completed: {self.result['content'][:50]}...")
        return shared
        
    def _run(self, shared):
        """Override _run to ensure proper handling of return values."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state
        self.post(shared, p, e)
        # Return the key for the next node, not the result
        return e


class SimpleOptimizationNode(Node):
    """Node for simple content optimization."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the optimization node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.successors = {}
        self.result = None
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for content optimization."""
        return {
            "content": shared.get("generated_content", ""),
            "keywords": shared.get("research_results", {}).get("keywords", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute content optimization."""
        # Simulate optimization
        time.sleep(1)
        
        content = prep_res.get("content", "")
        
        # Store results for post-processing
        self.result = {
            "optimized_content": f"Optimized: {content}",
            "recommendations": ["Add more keywords", "Improve readability"]
        }
        
        # Return the key for the next node to execute
        return "default"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Any) -> Dict[str, Any]:
        """Process optimization results and update the shared state."""
        # Update the shared state with optimization results
        shared["optimized_content"] = self.result["optimized_content"]
        shared["optimization_recommendations"] = self.result["recommendations"]
        shared["optimization_completed"] = True
        print(f"Content optimization completed: {self.result['optimized_content'][:50]}...")
        return shared
        
    def _run(self, shared):
        """Override _run to ensure proper handling of return values."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state
        self.post(shared, p, e)
        # Return the key for the next node, not the result
        return e


def create_marketing_workflow():
    """Create a simple marketing workflow."""
    # Create nodes
    research = SimpleResearchNode()
    generation = SimpleContentGenerationNode()
    optimization = SimpleOptimizationNode()
    
    # Connect nodes
    research.add_successor(generation)
    generation.add_successor(optimization)
    
    # Create flow starting with research
    flow = Flow(research)
    
    return flow


def main():
    """Run the marketing workflow example."""
    print("\n=== Simple PocketFlow Marketing Workflow Example ===\n")
    
    # Create workflow
    workflow = create_marketing_workflow()
    
    # Initial shared state
    store = {
        "topic": "AI in Marketing Automation",
        "content_type": "blog post",
        "target_audience": "marketing professionals"
    }
    
    # Run the workflow
    print("Running marketing workflow...")
    shared_state = store.copy()
    result = workflow.run(shared_state)
    
    # Display final results
    print("\nWorkflow completed!")
    print("\nFinal optimized content:")
    print(f"\n{shared_state.get('optimized_content', 'No content generated')}\n")
    
    print("Optimization recommendations:")
    for rec in shared_state.get("optimization_recommendations", []):
        print(f"- {rec}")


if __name__ == "__main__":
    main()
