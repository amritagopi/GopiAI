"""
Orchestration layer for combining PocketFlow and Open Manus workflows.

This module provides high-level orchestration capabilities that leverage both
PocketFlow's structured workflow system and Open Manus's agent-based planning.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Type
import sys
import os
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import Open Manus dependencies
from app.agent.base import BaseAgent
from app.tool.base import BaseTool

# Import our PocketFlow core classes
from app.pocketflow.core import Node, Flow, BatchNode
from app.pocketflow.adapters import (
    PocketFlowNodeAdapter, 
    OpenManusToolAdapter,
    PocketFlowAdapter,
    OpenManusFlowAdapter,
    BaseFlow
)


class WorkflowOrchestrator:
    """
    Orchestrates complex workflows that combine PocketFlow and Open Manus.
    
    This class acts as a high-level interface for creating, managing, and executing
    workflows that leverage both frameworks, enabling more complex agent-based systems.
    """
    
    def __init__(self, store: Dict[str, Any] = None):
        """
        Initialize a workflow orchestrator.
        
        Args:
            store: Optional initial shared state for the orchestrator
        """
        self.store = store or {}
        self.flows = {}
        self.pf_flows = {}
        self.agents = {}
        self.tools = {}
        
    def register_agent(self, agent: BaseAgent, name: Optional[str] = None) -> str:
        """Register an Open Manus agent with the orchestrator."""
        agent_name = name or agent.__class__.__name__
        self.agents[agent_name] = agent
        return agent_name
    
    def register_tool(self, tool: BaseTool, name: Optional[str] = None) -> str:
        """Register an Open Manus tool with the orchestrator."""
        tool_name = name or tool.__class__.__name__
        self.tools[tool_name] = tool
        return tool_name
    
    def register_pocketflow(self, flow: Flow, name: Optional[str] = None) -> str:
        """Register a PocketFlow flow with the orchestrator."""
        flow_name = name or flow.name
        self.pf_flows[flow_name] = flow
        return flow_name
    
    def register_flow(self, flow: BaseFlow, name: Optional[str] = None) -> str:
        """Register an Open Manus flow with the orchestrator."""
        flow_name = name or flow.name
        self.flows[flow_name] = flow
        return flow_name
    
    def create_planning_workflow(
        self,
        planner_agent: Optional[BaseAgent] = None,
        execution_tools: List[BaseTool] = None,
        flow_name: str = "PlanningWorkflow"
    ) -> BaseFlow:
        """
        Create a workflow that uses planning to orchestrate tool execution.
        
        Args:
            planner_agent: Agent responsible for planning (defaults to PlanningAgent)
            execution_tools: Tools available for plan execution
            flow_name: Name for the created flow
            
        Returns:
            A flow that combines planning and execution using both frameworks
        """
        # Use default planning agent if none provided
        if planner_agent is None:
            planner_agent = PlanningAgent()
        
        # Use all registered tools if none specified
        if execution_tools is None:
            execution_tools = list(self.tools.values())
        
        # Create a planning flow
        planning_flow = PlanningFlow(
            agent=planner_agent,
            tools=execution_tools,
            name=flow_name
        )
        
        # Register and return the flow
        self.register_flow(planning_flow, flow_name)
        return planning_flow
    
    def create_agent_workflow(
        self,
        agents: List[BaseAgent],
        connections: Dict[str, List[str]] = None,
        flow_name: str = "AgentWorkflow"
    ) -> Flow:
        """
        Create a PocketFlow workflow that orchestrates multiple agents.
        
        Args:
            agents: List of agents to include in the workflow
            connections: Optional mapping of source agents to target agents
                        (if None, agents will be connected sequentially)
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that orchestrates the agents
        """
        # Create PocketFlow nodes for each agent
        nodes = [PocketFlowNodeAdapter(agent) for agent in agents]
        flow = Flow(nodes=nodes, name=flow_name)
        
        # Configure connections
        if connections:
            for source, targets in connections.items():
                for target in targets:
                    flow.connect(source, target)
        else:
            # Sequential connection
            for i in range(len(nodes) - 1):
                flow.connect(nodes[i].name, nodes[i + 1].name)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    def create_hybrid_workflow(
        self,
        planning_agent: BaseAgent,
        execution_agents: List[BaseAgent],
        execution_tools: List[BaseTool] = None,
        flow_name: str = "HybridWorkflow"
    ) -> Flow:
        """
        Create a hybrid workflow that combines planning and agent orchestration.
        
        This creates a workflow where a planning agent determines which agents
        and tools to execute, and in what order.
        
        Args:
            planning_agent: Agent responsible for planning
            execution_agents: Agents available for execution
            execution_tools: Tools available for execution
            flow_name: Name for the created flow
            
        Returns:
            A PocketFlow Flow that implements the hybrid workflow
        """
        # Make all agents and tools available to the planning agent
        all_tools = execution_tools or []
        
        # Wrap all execution agents as tools that the planner can use
        for agent in execution_agents:
            agent_tool = OpenManusToolAdapter(
                PocketFlowNodeAdapter(agent),
                name=f"{agent.__class__.__name__}Tool",
                description=f"Execute the {agent.__class__.__name__} agent"
            )
            all_tools.append(agent_tool)
        
        # Create a planning flow
        planning_flow = self.create_planning_workflow(
            planner_agent=planning_agent,
            execution_tools=all_tools,
            flow_name=f"{flow_name}Planner"
        )
        
        # Wrap the planning flow as a PocketFlow node
        planning_node = PocketFlowNodeAdapter(
            planning_flow,
            input_keys=["task", "context"],
            output_key="plan_result",
            name="PlanningNode"
        )
        
        # Create a simple flow with just the planning node
        flow = Flow(nodes=[planning_node], name=flow_name)
        
        # Register and return the flow
        self.register_pocketflow(flow, flow_name)
        return flow
    
    async def run_workflow(
        self, 
        workflow_name: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a registered workflow with the given inputs.
        
        Args:
            workflow_name: Name of the workflow to run
            inputs: Input data for the workflow
            
        Returns:
            The results of the workflow execution
        """
        # Update the shared store with the inputs
        self.store.update(inputs)
        
        # Check if it's a PocketFlow or Open Manus flow
        if workflow_name in self.pf_flows:
            # Run PocketFlow
            flow = self.pf_flows[workflow_name]
            result = flow.run(self.store)
            self.store.update(result)
            return result
        elif workflow_name in self.flows:
            # Run Open Manus Flow
            flow = self.flows[workflow_name]
            result = await flow.run(**inputs)
            if isinstance(result, dict):
                self.store.update(result)
            return result
        else:
            raise ValueError(f"Workflow '{workflow_name}' not found")