"""
Fixed orchestrator for PocketFlow integration.

This module provides a fixed orchestrator for integrating Open Manus tools and agents
with PocketFlow, ensuring proper execution flow and avoiding circular dependencies.
"""
from typing import Any, Dict, List, Optional, Union
import copy
import logging

from pocketflow_framework import Flow, BaseNode

from app.agent.base import BaseAgent
from app.flow.base import BaseFlow
from app.tool.base import BaseTool
from app.pocketflow.fixed_adapters import ToolNode, AgentNode, PocketFlowNode

# Configure logging
logger = logging.getLogger(__name__)


class CustomFlow(Flow):
    """Custom Flow implementation that returns the shared state."""
    
    def __init__(self, start=None):
        """Initialize a custom flow with an optional start node."""
        super().__init__(start)
    
    def run(self, shared):
        """Override run to return the shared state."""
        # Call the parent's _run method
        self._run(shared)
        # Return the shared state
        return shared


class WorkflowOrchestrator:
    """
    Orchestrator for managing workflows combining Open Manus and PocketFlow.
    
    This class provides methods for registering tools and agents, creating
    workflows, and running them with the specified inputs.
    """
    
    def __init__(self, store: Dict[str, Any] = None):
        """
        Initialize a workflow orchestrator.
        
        Args:
            store: Optional initial shared state for the orchestrator
        """
        self.store = store or {}
        self.tools = {}
        self.agents = {}
        self.flows = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool with the orchestrator.
        
        Args:
            tool: The tool to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: The agent to register
        """
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def register_flow(self, flow: BaseFlow, name: str) -> None:
        """
        Register a flow with the orchestrator.
        
        Args:
            flow: The flow to register
            name: Name for the flow
        """
        self.flows[name] = flow
        logger.info(f"Registered flow: {name}")
    
    def create_tool_node(self, tool_name: str, output_key: str = None) -> ToolNode:
        """
        Create a PocketFlow node for a registered tool.
        
        Args:
            tool_name: Name of the registered tool
            output_key: Optional key to store the output under
            
        Returns:
            A PocketFlow node for the tool
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        return ToolNode(tool, output_key=output_key or tool_name)
    
    def create_agent_node(self, agent_name: str, output_key: str = None) -> AgentNode:
        """
        Create a PocketFlow node for a registered agent.
        
        Args:
            agent_name: Name of the registered agent
            output_key: Optional key to store the output under
            
        Returns:
            A PocketFlow node for the agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        agent = self.agents[agent_name]
        return AgentNode(agent, output_key=output_key or agent_name)
    
    def create_sequential_workflow(
        self,
        nodes: List[Union[ToolNode, AgentNode, PocketFlowNode]],
        flow_name: str
    ) -> CustomFlow:
        """
        Create a sequential workflow from the provided nodes.
        
        Args:
            nodes: List of nodes to include in the workflow
            flow_name: Name for the workflow
            
        Returns:
            A PocketFlow flow representing the sequential workflow
        """
        if not nodes:
            raise ValueError("No nodes provided for workflow")
        
        # Create a flow
        flow = CustomFlow()
        
        # Connect nodes sequentially
        for i in range(len(nodes) - 1):
            nodes[i].add_successor(nodes[i + 1])
        
        # Set the first node as the start node
        flow.start = nodes[0]
        
        # Register the flow
        self.flows[flow_name] = flow
        
        return flow
    
    def create_branching_workflow(
        self,
        nodes: Dict[str, Union[ToolNode, AgentNode, PocketFlowNode]],
        connections: Dict[str, Dict[str, str]],
        start_node: str,
        flow_name: str
    ) -> CustomFlow:
        """
        Create a branching workflow from the provided nodes and connections.
        
        Args:
            nodes: Dictionary of node name to node
            connections: Dictionary of node name to dictionary of action to next node name
            start_node: Name of the start node
            flow_name: Name for the workflow
            
        Returns:
            A PocketFlow flow representing the branching workflow
        """
        if not nodes:
            raise ValueError("No nodes provided for workflow")
        
        if start_node not in nodes:
            raise ValueError(f"Start node not found: {start_node}")
        
        # Create a flow
        flow = CustomFlow()
        
        # Connect nodes according to connections
        for node_name, actions in connections.items():
            if node_name not in nodes:
                raise ValueError(f"Node not found: {node_name}")
            
            node = nodes[node_name]
            
            for action, next_node_name in actions.items():
                if next_node_name not in nodes:
                    raise ValueError(f"Next node not found: {next_node_name}")
                
                next_node = nodes[next_node_name]
                node.add_successor(next_node, action)
        
        # Set the start node
        flow.start = nodes[start_node]
        
        # Register the flow
        self.flows[flow_name] = flow
        
        return flow
    
    def create_agent_workflow(
        self,
        agents: List[BaseAgent],
        connections: Dict[str, List[str]],
        flow_name: str
    ) -> CustomFlow:
        """
        Create a workflow from the provided agents and connections.
        
        Args:
            agents: List of agents to include in the workflow
            connections: Dictionary of agent name to list of next agent names
            flow_name: Name for the workflow
            
        Returns:
            A PocketFlow flow representing the agent workflow
        """
        if not agents:
            raise ValueError("No agents provided for workflow")
        
        # Create nodes for each agent
        nodes = {}
        for agent in agents:
            self.register_agent(agent)
            nodes[agent.name] = self.create_agent_node(agent.name)
        
        # Create a flow
        flow = CustomFlow()
        
        # Connect nodes according to connections
        for agent_name, next_agents in connections.items():
            if agent_name not in nodes:
                raise ValueError(f"Agent node not found: {agent_name}")
            
            node = nodes[agent_name]
            
            for next_agent_name in next_agents:
                if next_agent_name not in nodes:
                    raise ValueError(f"Next agent node not found: {next_agent_name}")
                
                next_node = nodes[next_agent_name]
                node.add_successor(next_node)
        
        # Set the first agent as the start node
        flow.start = nodes[agents[0].name]
        
        # Register the flow
        self.flows[flow_name] = flow
        
        return flow
    
    def run_workflow(
        self,
        workflow_name: str,
        inputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a registered workflow with the specified inputs.
        
        Args:
            workflow_name: Name of the registered workflow
            inputs: Optional inputs for the workflow
            
        Returns:
            The results from the workflow execution
        """
        if workflow_name not in self.flows:
            raise ValueError(f"Workflow not found: {workflow_name}")
        
        # Get the flow
        flow = self.flows[workflow_name]
        
        # Update the store with inputs
        if inputs:
            self.store.update(inputs)
        
        # Run the flow
        logger.info(f"Running workflow: {workflow_name}")
        result = flow.run(self.store)
        
        return result
