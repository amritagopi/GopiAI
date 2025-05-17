#!/usr/bin/env python3
"""
Custom Flow implementation for PocketFlow.
"""
import copy
import time
from typing import Dict, Any

from pocketflow_framework import Node, Flow, BaseNode


class CustomFlow(Flow):
    """Custom Flow implementation that returns the shared state."""
    
    def run(self, shared):
        """Override run to return the shared state."""
        # Call the parent's _run method
        self._run(shared)
        # Return the shared state
        return shared


class FixedNode(Node):
    """Fixed node implementation that correctly handles return values."""
    
    def __init__(self, name="node", max_retries=1, wait=0):
        """Initialize the node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
        self.exec_result = None
    
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
        self.exec_result = "default"
        return self.exec_result
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Post-process results."""
        print(f"[{self.name}] Post-processing...")
        shared[f"{self.name}_completed"] = True
        return shared
    
    def _run(self, shared):
        """Override _run to return the exec result, not the post result."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state but return exec result
        self.post(shared, p, e)
        return e


class ResearchNode(FixedNode):
    """Node for content research."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the research node."""
        super().__init__(name="research", max_retries=max_retries, wait=wait)
    
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
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process research results and update the shared state."""
        # Update the shared state with research results
        shared["research_results"] = self.result
        shared["research_completed"] = True
        print(f"Research completed. Found keywords: {self.result['keywords']}")
        return shared


class ContentGenerationNode(FixedNode):
    """Node for content generation."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the content generation node."""
        super().__init__(name="generation", max_retries=max_retries, wait=wait)
    
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
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process generation results and update the shared state."""
        # Update the shared state with generation results
        shared["generated_content"] = self.result["content"]
        shared["content_type"] = self.result["content_type"]
        shared["generation_completed"] = True
        print(f"Content generation completed: {self.result['content'][:50]}...")
        return shared


class OptimizationNode(FixedNode):
    """Node for content optimization."""
    
    def __init__(self, max_retries=1, wait=0):
        """Initialize the optimization node."""
        super().__init__(name="optimization", max_retries=max_retries, wait=wait)
    
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
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process optimization results and update the shared state."""
        # Update the shared state with optimization results
        shared["optimized_content"] = self.result["optimized_content"]
        shared["optimization_recommendations"] = self.result["recommendations"]
        shared["optimization_completed"] = True
        print(f"Content optimization completed: {self.result['optimized_content'][:50]}...")
        return shared


def create_marketing_workflow():
    """Create a marketing workflow."""
    # Create nodes
    research = ResearchNode()
    generation = ContentGenerationNode()
    optimization = OptimizationNode()
    
    # Connect nodes
    research.add_successor(generation)
    generation.add_successor(optimization)
    
    # Create flow starting with research
    flow = CustomFlow(research)
    
    return flow


def main():
    """Run the marketing workflow example."""
    print("\n=== Custom Flow Marketing Workflow Example ===\n")
    
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
    result = workflow.run(store)
    
    # Display final results
    print("\nWorkflow completed!")
    print("\nFinal optimized content:")
    print(f"\n{result.get('optimized_content', 'No content generated')}\n")
    
    print("Optimization recommendations:")
    for rec in result.get("optimization_recommendations", []):
        print(f"- {rec}")


if __name__ == "__main__":
    main()
