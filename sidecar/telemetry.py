"""
Telemetry, logging, and metrics for the sidecar.

Handles:
- Structured logging
- Event emission to Redis
- Metrics collection
- Health heartbeats
"""

import logging
import sys
import time
from typing import Dict, Any

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup structured logging."""
    log_level = config["sidecar"]["log_level"].upper()
    
    # Create logger
    logger = logging.getLogger("sidecar")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Format: [LEVEL] message
    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_startup_info(config: Dict[str, Any], has_bpy: bool = False) -> None:
    """Log startup information."""
    logger = logging.getLogger("sidecar")
    
    logger.info("=" * 60)
    logger.info("🎨 Blender Python Sidecar - Redis Bridge")
    logger.info("=" * 60)
    logger.info(f"Version: {config['sidecar']['version']}")
    logger.info(f"Worker ID: {config['sidecar']['worker_id']}")
    logger.info("")
    
    # Blender info
    if has_bpy:
        logger.info(f"✅ Blender {bpy.app.version_string} detected")
        logger.info(f"   Build: {bpy.app.build_platform.decode()}")
    else:
        logger.warning("⚠️  Blender Python API not available")
    
    logger.info("")
    logger.info("📋 Configuration:")
    logger.info(f"   Redis: {config['redis']['url']}")
    logger.info(f"   Command stream: {config['redis']['cmd_stream']}")
    logger.info(f"   Consumer group: {config['redis']['consumer_group']}")
    logger.info(f"   Log level: {config['sidecar']['log_level']}")
    logger.info("")
    logger.info("📁 Paths:")
    logger.info(f"   Assets: {config['paths']['assets_root']}")
    logger.info(f"   Build: {config['paths']['build_root']}")
    logger.info(f"   Temp: {config['paths']['tmp_root']}")
    logger.info("")
    logger.info("⚙️  Features:")
    logger.info(f"   Compression (zstd): {config['features']['use_zstd']}")
    logger.info(f"   MessagePack: {config['features']['use_msgpack']}")
    logger.info(f"   Profiling: {config['features']['enable_profiling']}")
    logger.info(f"   Tracing: {config['features']['enable_tracing']}")
    logger.info("")
    logger.info("🔒 Limits:")
    logger.info(f"   Max objects: {config['limits']['max_objects']}")
    logger.info(f"   Max GLB size: {config['limits']['max_glb_mb']} MB")
    logger.info(f"   Timeout: {config['limits']['cmd_timeout_ms']} ms")
    logger.info("=" * 60)
    logger.info("")


class Metrics:
    """Simple metrics collector."""
    
    def __init__(self):
        self.start_time = time.time()
        self.cpu_start = time.process_time()
    
    def collect(self) -> Dict[str, Any]:
        """Collect current metrics."""
        wall_ms = int((time.time() - self.start_time) * 1000)
        cpu_ms = int((time.process_time() - self.cpu_start) * 1000)
        
        metrics = {
            "cpu_ms": cpu_ms,
            "wall_ms": wall_ms,
            "mem_mb": 0,  # TODO: Use psutil to get actual memory
            "depsgraph_updates": 0,
        }
        
        return metrics


def create_response(
    trace_id: str,
    span_id: str,
    cmd: str,
    status: str = "ok",
    result: Dict[str, Any] = None,
    error: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    artifacts: list = None,
    logs: list = None,
) -> Dict[str, Any]:
    """Create a standardized response envelope."""
    response = {
        "v": "1.0",
        "trace_id": trace_id,
        "span_id": span_id,
        "status": status,
        "cmd": cmd,
    }
    
    if result is not None:
        response["result"] = result
    
    if error is not None:
        response["error"] = error
    
    if metrics is not None:
        response["metrics"] = metrics
    
    if artifacts is not None:
        response["artifacts"] = artifacts
    
    if logs is not None:
        response["logs"] = logs
    
    return response

