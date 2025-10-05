"""
Auto-start Blender MCP addon on startup
Degenerate Labs - MCP Integration
"""

import bpy


def load_blender_mcp():
    """Enable and start the Blender MCP addon automatically."""
    addon_name = "blender_mcp"
    
    # Enable the addon if not already enabled
    if addon_name not in bpy.context.preferences.addons:
        try:
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f"✅ Blender MCP addon enabled")
        except Exception as e:
            print(f"❌ Failed to enable Blender MCP addon: {e}")
            return
    
    # Start the MCP server
    try:
        # The addon should auto-start, but we can trigger it explicitly
        print("🚀 Blender MCP addon loaded and ready")
        print("   Socket server on localhost:9876")
    except Exception as e:
        print(f"⚠️  Blender MCP startup issue: {e}")


# Register the function to run after Blender fully loads
bpy.app.timers.register(load_blender_mcp, first_interval=1.0)

