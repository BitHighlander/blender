#!/usr/bin/env python3
"""
Blender Python Sidecar - Redis Bridge

Main entry point for the Blender sidecar service.
Run with: blender -b --python sidecar.py

Author: Generated
Version: 1.0.0-dev
"""

import sys
import logging
import time
import traceback
import site
from pathlib import Path

# Add user site-packages to path (for packages installed with pip --user)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ensure sidecar package is importable
sys.path.insert(0, str(Path(__file__).parent))

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("WARNING: bpy not available (running outside Blender)")

from sidecar.config import load_config
from sidecar.consumer import RedisConsumer
from sidecar.router import CommandRouter
from sidecar.telemetry import setup_logging, log_startup_info
from sidecar.errors import SidecarError


def main():
    """Main entry point for the sidecar."""
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    logger = setup_logging(config)
    
    # Log startup info
    log_startup_info(config, has_bpy=HAS_BPY)
    
    if not HAS_BPY:
        logger.error("Blender Python API (bpy) not available!")
        logger.error("This script must be run with: blender -b --python sidecar.py")
        sys.exit(1)
    
    # Initialize Blender environment
    logger.info("Initializing Blender environment...")
    if config["blender"]["disable_undo"]:
        logger.debug("Disabling global undo...")
        bpy.context.preferences.edit.use_global_undo = False
    
    # Initialize command router
    router = CommandRouter(config)
    
    # Initialize Redis consumer
    consumer = RedisConsumer(config, router)
    
    # Start consuming commands (non-blocking, runs in background thread)
    logger.info("🚀 Sidecar ready! Starting consumer...")
    logger.info(f"📬 Command stream: {config['redis']['cmd_stream']}")
    logger.info(f"📤 Reply stream: {config['redis']['reply_stream_default']}")
    logger.info(f"👤 Worker ID: {config['sidecar']['worker_id']}")
    logger.info("")
    logger.info("✨ Using bpy.app.timers for real-time, non-blocking execution!")
    logger.info("   Blender viewport will stay responsive.")
    logger.info("")
    logger.info("Press Ctrl+C to stop gracefully.")
    
    try:
        # Start background consumer thread
        consumer.run()
        
        # Keep main thread alive (but responsive) while consumer runs
        consumer.wait_forever()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Received interrupt signal, shutting down gracefully...")
        consumer.shutdown()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("✅ Sidecar shut down successfully.")


if __name__ == "__main__":
    main()

