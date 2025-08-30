"""
Fallback gopiai_integration package.
Provides minimal stubs for missing integration.
"""

class ModelProvider:
    """Fallback ModelProvider stub."""
    def __init__(self, *args, **kwargs):
        pass

def get_model_config_manager():
    """Return empty config manager."""
    return {}

def get_openrouter_client():
    """Return None as placeholder for OpenRouter client."""
    return None