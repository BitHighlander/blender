"""
Blender Sidecar - Auto-start on Launch

This script automatically starts the Redis sidecar when Blender launches.
"""

import bpy
import threading
import sys
import site
from pathlib import Path

# Add user site-packages to path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

def start_sidecar():
    """Start the sidecar in a background thread."""
    # Import sidecar modules
    from sidecar.config import load_config
    from sidecar.consumer import RedisConsumer
    from sidecar.router import CommandRouter
    from sidecar.telemetry import setup_logging
    
    print("\n" + "="*60)
    print("🎨 Starting Blender Sidecar Bridge...")
    print("="*60)
    
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        logger = setup_logging(config)
        
        # Disable undo during operations
        if config["blender"]["disable_undo"]:
            bpy.context.preferences.edit.use_global_undo = False
        
        # Initialize command router
        router = CommandRouter(config)
        
        # Initialize Redis consumer
        consumer = RedisConsumer(config, router)
        
        # Start consumer loop in background thread
        def run_consumer():
            try:
                consumer.run()
            except Exception as e:
                print(f"❌ Sidecar error: {e}")
        
        thread = threading.Thread(target=run_consumer, daemon=True)
        thread.start()
        
        print("✅ Sidecar running in background")
        print("="*60 + "\n")
        
    except ImportError as e:
        print(f"⚠️  Sidecar dependencies not installed: {e}")
        print("   Install with: pip install redis python-dotenv")
    except Exception as e:
        print(f"❌ Failed to start sidecar: {e}")
        import traceback
        traceback.print_exc()


def register():
    """Called when Blender starts."""
    # Add sidecar package to path
    repo_root = Path(__file__).parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    
    # Start sidecar in background
    start_sidecar()


def unregister():
    """Called when Blender exits."""
    pass


# Auto-register on import (startup scripts are imported automatically)
if __name__ != "__main__":
    register()

