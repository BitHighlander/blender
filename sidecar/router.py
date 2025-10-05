"""
Command router for the sidecar.

Routes incoming commands to their respective handlers.
"""

import logging
from typing import Dict, Any, Callable

from .errors import SidecarError, CommandError
from .commands.ping import handle_ping
from .commands.mesh import handle_create_cube, handle_create_room
from .commands.dungeon_simple import create_simple_dungeon


class CommandRouter:
    """Routes commands to handlers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("sidecar")
        
        # Command registry: cmd_name -> handler_function
        self.handlers: Dict[str, Callable] = {
            "Ping": handle_ping,
            "CreateCube": handle_create_cube,
            "CreateRoom": handle_create_room,
            # Simple dungeon that just works! 🏰
            "CreateDungeon": create_simple_dungeon,
        }
        
        # Debug: log registered commands at startup
        self.logger.info(f"🏰 Registered {len(self.handlers)} commands: {', '.join(sorted(self.handlers.keys()))}")
    
    def route(self, cmd: str, params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a command to its handler.
        
        Args:
            cmd: Command name
            params: Command parameters
            opts: Command options
        
        Returns:
            Result dictionary
        
        Raises:
            CommandError: If command is unknown or handler fails
        """
        handler = self.handlers.get(cmd)
        
        if handler is None:
            raise CommandError(
                code="E_UNKNOWN_COMMAND",
                message=f"Unknown command: {cmd}",
                details={"cmd": cmd},
                retryable=False,
            )
        
        self.logger.debug(f"Routing command: {cmd}")
        
        try:
            result = handler(self.config, params, opts)
            return result
        except SidecarError:
            # Re-raise sidecar errors as-is
            raise
        except Exception as e:
            # Wrap unexpected errors
            self.logger.error(f"Handler error for {cmd}: {e}", exc_info=True)
            raise CommandError(
                code="E_INTERNAL",
                message=f"Internal error executing {cmd}: {str(e)}",
                details={"cmd": cmd, "error": str(e)},
                retryable=True,
            )
    
    def register_handler(self, cmd: str, handler: Callable) -> None:
        """Register a new command handler."""
        self.handlers[cmd] = handler
        self.logger.debug(f"Registered handler for command: {cmd}")
    
    def list_commands(self) -> list:
        """List all registered commands."""
        return sorted(self.handlers.keys())

