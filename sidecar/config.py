"""
Configuration management for the sidecar.

Loads configuration from:
1. Default values
2. sidecar_config.toml (if exists)
3. .env file (if exists)
4. Environment variables (highest priority)
"""

import os
import socket
from pathlib import Path
from typing import Dict, Any

try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


def get_default_config() -> Dict[str, Any]:
    """Return default configuration for development."""
    hostname = socket.gethostname()
    
    return {
        "redis": {
            "url": "redis://localhost:6379/0",
            "cmd_stream": "blender:cmd",
            "reply_stream_default": "blender:reply",
            "events_stream": "blender:events",
            "metrics_stream": "blender:metrics",
            "health_key_prefix": "blender:health",
            "consumer_group": "cg:dev",
            "consumer_name": f"worker-{hostname}",
        },
        "sidecar": {
            "worker_id": hostname,
            "log_level": "DEBUG",
            "version": "2.0.0-realtime",  # Real-time threading with bpy.app.timers!
        },
        "paths": {
            "assets_root": "./assets",
            "build_root": "./build",
            "tmp_root": "./tmp",
            "allowed_read_paths": ["./assets", "./build"],
            "allowed_write_paths": ["./build", "./tmp"],
        },
        "features": {
            "use_zstd": False,
            "use_msgpack": False,
            "allow_ops_fallback": True,
            "enable_profiling": True,
            "enable_tracing": True,
        },
        "limits": {
            "max_objects": 10000,
            "max_glb_mb": 100,
            "cmd_timeout_ms": 60000,
            "heartbeat_interval_sec": 10,
            "max_batch_ops": 100,
        },
        "blender": {
            "disable_undo": True,
            "startup_blend": "",
            "temp_blend_prefix": "sidecar_",
        },
    }


def load_toml_config(path: Path) -> Dict[str, Any]:
    """Load configuration from TOML file."""
    if not HAS_TOML:
        return {}
    
    if not path.exists():
        return {}
    
    try:
        return toml.load(path)
    except Exception as e:
        print(f"WARNING: Failed to load {path}: {e}")
        return {}


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}
    
    # Redis
    if os.getenv("REDIS_URL"):
        config.setdefault("redis", {})["url"] = os.getenv("REDIS_URL")
    if os.getenv("REDIS_CMD_STREAM"):
        config.setdefault("redis", {})["cmd_stream"] = os.getenv("REDIS_CMD_STREAM")
    if os.getenv("REDIS_REPLY_STREAM"):
        config.setdefault("redis", {})["reply_stream_default"] = os.getenv("REDIS_REPLY_STREAM")
    if os.getenv("REDIS_EVENTS_STREAM"):
        config.setdefault("redis", {})["events_stream"] = os.getenv("REDIS_EVENTS_STREAM")
    if os.getenv("REDIS_METRICS_STREAM"):
        config.setdefault("redis", {})["metrics_stream"] = os.getenv("REDIS_METRICS_STREAM")
    if os.getenv("REDIS_CONSUMER_GROUP"):
        config.setdefault("redis", {})["consumer_group"] = os.getenv("REDIS_CONSUMER_GROUP")
    if os.getenv("REDIS_CONSUMER_NAME"):
        config.setdefault("redis", {})["consumer_name"] = os.getenv("REDIS_CONSUMER_NAME")
    
    # Sidecar
    if os.getenv("SIDECAR_WORKER_ID"):
        config.setdefault("sidecar", {})["worker_id"] = os.getenv("SIDECAR_WORKER_ID")
    if os.getenv("SIDECAR_LOG_LEVEL"):
        config.setdefault("sidecar", {})["log_level"] = os.getenv("SIDECAR_LOG_LEVEL")
    if os.getenv("SIDECAR_VERSION"):
        config.setdefault("sidecar", {})["version"] = os.getenv("SIDECAR_VERSION")
    
    # Paths
    if os.getenv("PATHS_ASSETS_ROOT"):
        config.setdefault("paths", {})["assets_root"] = os.getenv("PATHS_ASSETS_ROOT")
    if os.getenv("PATHS_BUILD_ROOT"):
        config.setdefault("paths", {})["build_root"] = os.getenv("PATHS_BUILD_ROOT")
    if os.getenv("PATHS_TMP_ROOT"):
        config.setdefault("paths", {})["tmp_root"] = os.getenv("PATHS_TMP_ROOT")
    
    # Features
    if os.getenv("FEATURES_USE_ZSTD"):
        config.setdefault("features", {})["use_zstd"] = os.getenv("FEATURES_USE_ZSTD").lower() == "true"
    if os.getenv("FEATURES_USE_MSGPACK"):
        config.setdefault("features", {})["use_msgpack"] = os.getenv("FEATURES_USE_MSGPACK").lower() == "true"
    if os.getenv("FEATURES_ALLOW_OPS_FALLBACK"):
        config.setdefault("features", {})["allow_ops_fallback"] = os.getenv("FEATURES_ALLOW_OPS_FALLBACK").lower() == "true"
    if os.getenv("FEATURES_ENABLE_PROFILING"):
        config.setdefault("features", {})["enable_profiling"] = os.getenv("FEATURES_ENABLE_PROFILING").lower() == "true"
    if os.getenv("FEATURES_ENABLE_TRACING"):
        config.setdefault("features", {})["enable_tracing"] = os.getenv("FEATURES_ENABLE_TRACING").lower() == "true"
    
    # Limits
    if os.getenv("LIMITS_MAX_OBJECTS"):
        config.setdefault("limits", {})["max_objects"] = int(os.getenv("LIMITS_MAX_OBJECTS"))
    if os.getenv("LIMITS_MAX_GLB_MB"):
        config.setdefault("limits", {})["max_glb_mb"] = int(os.getenv("LIMITS_MAX_GLB_MB"))
    if os.getenv("LIMITS_CMD_TIMEOUT_MS"):
        config.setdefault("limits", {})["cmd_timeout_ms"] = int(os.getenv("LIMITS_CMD_TIMEOUT_MS"))
    if os.getenv("LIMITS_HEARTBEAT_INTERVAL_SEC"):
        config.setdefault("limits", {})["heartbeat_interval_sec"] = int(os.getenv("LIMITS_HEARTBEAT_INTERVAL_SEC"))
    if os.getenv("LIMITS_MAX_BATCH_OPS"):
        config.setdefault("limits", {})["max_batch_ops"] = int(os.getenv("LIMITS_MAX_BATCH_OPS"))
    
    # Blender
    if os.getenv("BLENDER_DISABLE_UNDO"):
        config.setdefault("blender", {})["disable_undo"] = os.getenv("BLENDER_DISABLE_UNDO").lower() == "true"
    if os.getenv("BLENDER_STARTUP_BLEND"):
        config.setdefault("blender", {})["startup_blend"] = os.getenv("BLENDER_STARTUP_BLEND")
    if os.getenv("BLENDER_TEMP_BLEND_PREFIX"):
        config.setdefault("blender", {})["temp_blend_prefix"] = os.getenv("BLENDER_TEMP_BLEND_PREFIX")
    
    return config


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merge override dict into base dict."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config() -> Dict[str, Any]:
    """
    Load configuration from all sources.
    
    Priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. sidecar_config.toml
    4. Default values
    """
    # Start with defaults
    config = get_default_config()
    
    # Merge TOML config
    toml_path = Path("sidecar_config.toml")
    toml_config = load_toml_config(toml_path)
    if toml_config:
        config = deep_merge(config, toml_config)
    
    # Load .env file
    if HAS_DOTENV:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
    
    # Merge environment variables (highest priority)
    env_config = load_env_config()
    if env_config:
        config = deep_merge(config, env_config)
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration and raise if invalid."""
    # TODO: Add validation logic
    # - Check Redis URL format
    # - Verify paths exist
    # - Validate limits are reasonable
    pass

