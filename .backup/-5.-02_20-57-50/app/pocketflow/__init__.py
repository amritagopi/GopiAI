"""
PocketFlow integration for Open Manus.

This module provides adapters and utilities to integrate PocketFlow with Open Manus,
allowing for complex workflow orchestration combining both frameworks' strengths.
"""

# First, check if PocketFlow is available
import os
import sys
import importlib.util

# Check if PocketFlow is available
POCKETFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'PocketFlow')
sys.path.append(POCKETFLOW_DIR)

try:
    import pocketflow_framework
    POCKETFLOW_AVAILABLE = True
except ImportError:
    POCKETFLOW_AVAILABLE = False

# Import core components - these will work whether or not PocketFlow is available
from app.pocketflow.core import Node, Flow, BatchNode
from app.pocketflow.adapters import PocketFlowNodeAdapter, OpenManusToolAdapter, PocketFlowAdapter
from app.pocketflow.orchestrator import WorkflowOrchestrator

__all__ = [
    "POCKETFLOW_AVAILABLE",
    "Node", 
    "Flow", 
    "BatchNode",
    "PocketFlowNodeAdapter", 
    "OpenManusToolAdapter", 
    "PocketFlowAdapter",
    "WorkflowOrchestrator"
]