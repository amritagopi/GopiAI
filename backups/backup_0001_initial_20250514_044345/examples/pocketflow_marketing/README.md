# PocketFlow Marketing Automation Examples

This directory contains examples of using the PocketFlow framework for marketing automation workflows.

## Overview

These examples demonstrate how to use PocketFlow to create marketing automation workflows, including content research, generation, optimization, distribution, and analytics.

## Dependencies

These examples require the `pocketflow_framework` package, which is a lightweight workflow orchestration system. You can install it using pip:

```bash
pip install pocketflow_framework
```

The examples also rely on the Manus framework's marketing components, which provide the tools and agents used in the workflows.

## PocketFlow-Manus Integration

The examples in this directory showcase the integration between PocketFlow and Manus. This integration allows you to:

1. **Use Manus Tools in PocketFlow Workflows**: The marketing tools from Manus are adapted to work as PocketFlow nodes.
2. **Create Complex Marketing Workflows**: Build sophisticated marketing automation workflows by connecting nodes for different marketing tasks.
3. **Manage Shared State**: Pass data between nodes using a shared state dictionary, allowing for seamless data flow throughout the workflow.
4. **Extend with Custom Nodes**: Create custom nodes for specific marketing tasks by extending the base classes.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic example showing how to create and run a simple marketing workflow with PocketFlow.

### 2. Documentation Example (`doc_example.py`)

An example based on the PocketFlow documentation, showing how to use the framework with nodes and workflow execution.

### 3. Debug Example (`debug_example.py`)

A debugging version of the example to trace execution and identify issues related to the handling of return values from nodes.

### 4. Fixed Example (`fixed_example.py`)

A fixed version of the marketing workflow example that correctly handles return values from node executions and ensures proper workflow completion.

### 5. Custom Flow Example (`custom_flow.py`)

An example that implements a custom Flow class that returns the shared state, allowing for better data flow between nodes.

### 6. Complete Example (`complete_example.py`)

A comprehensive example that demonstrates a complete marketing workflow from research to analytics, using the fixed implementation of PocketFlow integration.

## Key Components

- **Nodes**: Each node in the workflow represents a specific marketing task, such as research, content generation, or optimization.
- **Flow**: The flow connects nodes and manages the execution of the workflow.
- **Shared State**: Data is passed between nodes using a shared state dictionary.
- **Orchestrator**: The orchestrator manages the creation and execution of workflows.

## Usage

To run any of the examples, use the following command:

```bash
python3 examples/pocketflow_marketing/<example_file>.py
```

For example:

```bash
python3 examples/pocketflow_marketing/complete_example.py
```

## Implementation Details

The examples use the following components from the Manus codebase:

- `app.marketing.fixed_nodes`: Contains the fixed implementation of marketing-specific nodes.
- `app.marketing.fixed_orchestrator`: Contains the fixed implementation of the marketing orchestrator.
- `app.marketing.tools`: Contains the tools used by the marketing nodes.

These components are designed to work with the PocketFlow framework, which provides the core functionality for creating and executing workflows.

## Troubleshooting

If you encounter issues with the examples, check the following:

1. Make sure the PocketFlow framework is installed and accessible:
   ```bash
   pip install pocketflow_framework
   ```

2. Verify that the node implementations correctly handle return values and shared state.
3. Check that the flow is properly configured to return the shared state.
4. Ensure that the Manus framework is properly installed and configured.

## Contributing

Feel free to extend these examples or create new ones to demonstrate additional marketing automation capabilities.
