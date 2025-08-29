"""
Fallback implementation of the ansi2html module.

Provides a minimal Ansi2HTMLConverter that strips ANSI escape sequences
from a given text. This allows the application to import the module
without requiring the external dependency.
"""

import re
from typing import Any

class Ansi2HTMLConverter:
    """Simple converter that removes ANSI escape codes."""

    def __init__(self, *args, **kwargs):
        pass

    def convert(self, text: str, full: bool = True) -> str:
        """
        Strip ANSI escape sequences from *text*.

        Args:
            text: Input string possibly containing ANSI codes.
            full: Ignored – kept for API compatibility.

        Returns:
            The input string with all ANSI escape sequences removed.
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# Export name expected by the UI code
__all__ = ["Ansi2HTMLConverter"]