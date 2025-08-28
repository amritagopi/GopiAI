# GopiAI Architecture

This document provides an overview of the GopiAI architecture after the refactoring to use native CrewAI tools.

## Core Components

### 1. Model Management

- **Model Configuration**: Centralized configuration for all supported models
- **Model Switching**: Dynamic switching between different LLM providers and models
- **Provider Support**: Native support for OpenAI, Anthropic, and other providers

### 2. Tool Integration

- **Base Tool Class**: Abstract base class for all tools
- **Built-in Tools**: Common tools like web search and file operations
- **Custom Tools**: Framework for adding custom tools

### 3. Configuration

- **Centralized Config**: Single source of truth for all configurations
- **Environment Variables**: Secure handling of API keys and sensitive data
- **Model Registry**: Registry of available models and their configurations

## Key Changes from Previous Version

1. **Removed Dependencies**:
   - Removed custom `gopiai_integration` module
   - Eliminated redundant code and dependencies

2. **Simplified Architecture**:
   - Using native CrewAI tools and components
   - Reduced complexity and maintenance overhead

3. **Improved Maintainability**:
   - Better code organization
   - Clear separation of concerns
   - Comprehensive test coverage

## Getting Started

### Prerequisites

- Python 3.8+
- CrewAI
- Required API keys for your chosen providers

### Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Example

```python
from crewai_tools import model_manager, tool_manager

# List available models
models = model_manager.get_available_models()
print("Available models:", [m.model_id for m in models])

# Set current model
model_manager.set_current_model("openai/gpt-4")

# Get all available tools
tools = tool_manager.get_all_tools()
print("Available tools:", [t.name for t in tools])
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all required environment variables are set
   - Check `.env` file for missing configurations

2. **Model Not Found**
   - Verify the model ID is correct
   - Check if the provider is properly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

[Your License Here]
