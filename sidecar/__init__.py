"""
Blender Sidecar - Redis Bridge Package

A minimal Python sidecar that runs inside headless Blender and exposes
a stable, efficient command API over Redis Streams.
"""

__version__ = "1.0.0-dev"
__author__ = "Generated"

from .config import load_config
from .router import CommandRouter
from .consumer import RedisConsumer
from .errors import SidecarError, CommandError

__all__ = [
    "load_config",
    "CommandRouter",
    "RedisConsumer",
    "SidecarError",
    "CommandError",
]

