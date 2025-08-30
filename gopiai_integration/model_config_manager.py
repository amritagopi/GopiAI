"""
Fallback implementation for the model configuration manager.

This module provides a minimal stub that mimics the public API expected
by the UI components (UnifiedModelWidget, OpenRouterModelWidget, etc.).
The real implementation lives in the CrewAI tools, but for the purpose
of running the GopiAI UI without the original package we only need a
few simple methods:

- ``get_models(provider=None)`` – returns an empty list.
- ``get_model_info(model_id)`` – returns a dictionary with the
  requested ``model_id`` and placeholder fields.
- ``set_current_configuration(provider, model_id)`` – a no‑op that
  returns ``True`` to indicate success.
- ``get_current_configuration()`` – returns ``None`` (no active config).

All methods are deliberately lightweight and contain no external
dependencies, so the UI can import this module without raising
``ImportError``. The stub can be extended later if more functionality
is required.
"""

from enum import Enum
from typing import List, Dict, Any, Optional

class ModelProvider(Enum):
    """Enum mirroring the real provider enum."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class DummyConfigManager:
    """Very small stand‑in for the real ConfigManager."""

    def get_models(self, provider: Optional[ModelProvider] = None) -> List[Dict[str, Any]]:
        """
        Return a list of model descriptors.
        The real implementation would query the backend; here we simply
        return an empty list to keep UI code functional.
        """
        return []

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Return a placeholder description for a model.
        """
        return {
            "id": model_id,
            "name": model_id,
            "description": "No model information available (fallback).",
            "provider": "unknown",
        }

    # The UI expects a ``set_current_configuration`` method that returns
    # a boolean indicating success.
    def set_current_configuration(self, provider: ModelProvider, model_id: str) -> bool:
        return True

    # The UI may call ``get_current_configuration``; we return ``None``
    # to indicate that no configuration is active.
    def get_current_configuration(self) -> Optional[Any]:
        return None


def get_model_config_manager() -> DummyConfigManager:
    """
    Factory function used by the UI to obtain a config manager instance.
    """
    return DummyConfigManager()