"""
Fallback stub for the original `gopiai_integration.openrouter_client`.

The real module provided a client for interacting with the OpenRouter API.
Here we supply a minimal placeholder that satisfies imports without
performing any network operations.
"""

def get_openrouter_client():
    """Return a dummy client (None) to keep UI code functional."""
    return None