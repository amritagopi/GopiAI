# Breaking Changes

This document outlines the breaking changes introduced in the latest version of GopiAI.

## Major Changes

### 1. Removed `gopia_integration` Module
- **Impact**: High
- **Description**: The custom `gopia_integration` module has been completely removed in favor of native CrewAI tools.
- **Migration**: Update all imports from `gopia_integration` to use the new `crewai_tools` module.

### 2. Updated Model Management
- **Impact**: High
- **Description**: The model management system has been completely redesigned.
- **Changes**:
  - New `ModelManager` class for managing model configurations
  - Simplified model switching interface
  - Updated configuration format
- **Migration**:
  ```python
  # Old way
  from gopia_integration.model_config_manager import ModelConfigurationManager
  
  # New way
  from crewai_tools.model_manager import model_manager
  ```

### 3. Tool System Changes
- **Impact**: Medium
- **Description**: The tool system has been updated to use CrewAI's native tool system.
- **Changes**:
  - New base classes for tools
  - Updated tool registration
  - Simplified tool configuration
- **Migration**:
  ```python
  # Old way
  from gopia_integration.tools import BaseTool
  
  # New way
  from crewai.tools import BaseTool
  from crewai_tools.tool_integration import ToolIntegration
  ```

### 4. Configuration Changes
- **Impact**: Medium
- **Description**: Configuration system has been updated.
- **Changes**:
  - New configuration file format
  - Environment variable handling
  - Centralized configuration management
- **Migration**:
  - Update configuration files to match the new format
  - Set required environment variables

## Deprecations

The following features are deprecated and will be removed in a future version:

1. **Custom Tool Implementations**: Use CrewAI's native tools instead.
2. **Legacy Model Configuration**: Update to the new model configuration format.
3. **Direct API Calls**: Use the provided wrapper functions instead.

## Migration Guide

### Updating Imports

```python
# Old imports
from gopia_integration.model_config_manager import ModelConfigurationManager
from gopia_integration.tools import CustomTool

# New imports
from crewai_tools.model_manager import model_manager
from crewai.tools import BaseTool
```

### Updating Configuration

1. Update your configuration files to match the new format
2. Set required environment variables
3. Update any custom tool implementations

### Testing

After updating, thoroughly test:
1. Model switching functionality
2. Tool integration
3. Configuration loading
4. Error handling

## Known Issues

- Some third-party tool integrations may require updates
- Custom tools may need adjustments to work with the new system

## Getting Help

If you encounter any issues during migration, please:
1. Check the updated documentation
2. Review the example implementations
3. Open an issue on our GitHub repository

## Version Support

This version requires:
- Python 3.8+
- CrewAI 0.28.0+
- Additional dependencies as specified in requirements.txt
