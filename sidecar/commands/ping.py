"""
Ping command handler.

Simple health check command that echoes back the provided message.
"""

import socket
from typing import Dict, Any

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def handle_ping(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Ping command.
    
    Args:
        config: Sidecar configuration
        params: Command parameters
            - echo: Optional string to echo back
        opts: Command options
    
    Returns:
        Result dictionary with:
            - echo: Echoed message
            - blender_version: Blender version string
            - sidecar_version: Sidecar version
            - worker_id: Worker identifier
    """
    echo = params.get("echo", "pong")
    
    # Gather system info
    result = {
        "echo": echo,
        "sidecar_version": config["sidecar"]["version"],
        "worker_id": config["sidecar"]["worker_id"],
        "hostname": socket.gethostname(),
    }
    
    # Add Blender info if available
    if HAS_BPY:
        result["blender_version"] = bpy.app.version_string
        result["blender_build"] = bpy.app.build_platform.decode()
    else:
        result["blender_version"] = "unavailable"
        result["blender_build"] = "unavailable"
    
    return result

