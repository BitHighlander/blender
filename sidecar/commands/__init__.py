"""
Command handlers for the sidecar.

Each command is implemented as a separate module with a handle_* function.
"""

from .ping import handle_ping

__all__ = ["handle_ping"]

