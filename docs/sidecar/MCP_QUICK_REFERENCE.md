# MCP Integration Quick Reference

**Purpose:** Quick copy-paste code patterns for MCP integration  
**See Also:** [MCP_INTEGRATION_ANALYSIS.md](./MCP_INTEGRATION_ANALYSIS.md) for full analysis

---

## Essential Code Patterns

### 1. Thread-Safe Execution (Critical!)

```python
import bpy

def execute_in_main_thread(callback):
    """
    Execute callback in Blender's main thread.
    Source: blender-mcp/addon.py:166
    """
    def wrapper():
        try:
            result = callback()
            return None  # Return None to prevent re-execution
        except Exception as e:
            print(f"Error in main thread execution: {e}")
            return None
    
    bpy.app.timers.register(wrapper, first_interval=0.0)
```

**Usage:**
```python
def create_cube():
    bpy.ops.mesh.primitive_cube_add()
    
execute_in_main_thread(create_cube)
```

---

### 2. Singleton Server Pattern

```python
# Source: blendify/internal/singleton.py

class Singleton(type):
    """Metaclass that ensures only one instance of a class exists"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]
        else:
            raise RuntimeError(
                f"Only one instance of {cls.__name__} is allowed. "
                f"Use {cls.__name__}.get_instance() instead."
            )
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]
```

**Usage:**
```python
class MCPServer(metaclass=Singleton):
    def __init__(self):
        self.tools = []
        print("MCP Server initialized (singleton)")

# This works
server1 = MCPServer()

# This raises RuntimeError
# server2 = MCPServer()  # ERROR!
```

---

### 3. Safe Exit Decorator

```python
# Source: blendify/internal/execution_decorator.py

import sys
import traceback
from functools import wraps

_exit_bypassed = False

def safe_exit(func):
    """
    Decorator that catches exceptions and exits cleanly.
    Prevents Blender memory leak detection hang.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            global _exit_bypassed
            _exit_bypassed = True
            
            print(f"Error in {func.__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
            # Exit cleanly
            sys.exit(1)
    return wrapper
```

**Usage:**
```python
@safe_exit
def render_scene():
    """Rendering with safe error handling"""
    bpy.ops.render.render(write_still=True)
```

---

### 4. Stdout Capture Context Manager

```python
import sys
from contextlib import contextmanager
from io import StringIO

@contextmanager
def catch_stdout(skip=False):
    """
    Context manager to suppress or capture stdout.
    Source: blendify/internal/io.py
    """
    if skip:
        # Don't suppress - let output through
        yield None
    else:
        # Suppress stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            yield sys.stdout
        finally:
            sys.stdout = old_stdout
```

**Usage:**
```python
# Suppress Blender's chatty output
with catch_stdout():
    bpy.ops.render.render()

# Allow output (verbose mode)
with catch_stdout(skip=True):
    bpy.ops.render.render()
```

---

### 5. High-Level Scene API

```python
# Source: blendify/scene.py (adapted)

import bpy

class Scene(metaclass=Singleton):
    """High-level scene management"""
    
    def __init__(self):
        self._camera = None
        self._reset_scene()
    
    def _reset_scene(self):
        """Reset to empty scene"""
        bpy.ops.wm.read_homefile(use_empty=True)
        scene = bpy.data.scenes[0]
        scene.world = bpy.data.worlds.new("World")
    
    def clear(self):
        """Clear the scene"""
        self._reset_scene()
    
    @property
    def camera(self):
        return self._camera
    
    def set_camera(self, location, rotation):
        """Set camera with simple parameters"""
        if self._camera is None:
            bpy.ops.object.camera_add()
            self._camera = bpy.context.object
        
        self._camera.location = location
        self._camera.rotation_euler = rotation
        bpy.context.scene.camera = self._camera
        return self._camera

# Global scene instance
scene = Scene()
```

**Usage:**
```python
from blendify import scene

scene.clear()
scene.set_camera(location=(5, -5, 5), rotation=(0.8, 0, 0.8))
```

---

### 6. Collections Pattern

```python
# Source: blendify/renderables/collection.py (adapted)

class RenderablesCollection:
    """Collection of renderable objects"""
    
    def __init__(self):
        self.objects = []
    
    def add_cube(self, size=2.0, location=(0, 0, 0), name="Cube"):
        """Add a cube to the scene"""
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = bpy.context.object
        obj.name = name
        self.objects.append(obj)
        return obj
    
    def add_sphere(self, radius=1.0, location=(0, 0, 0), name="Sphere"):
        """Add a sphere to the scene"""
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
        obj = bpy.context.object
        obj.name = name
        self.objects.append(obj)
        return obj
    
    def clear(self):
        """Remove all objects"""
        for obj in self.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.objects.clear()

class LightsCollection:
    """Collection of light objects"""
    
    def __init__(self):
        self.lights = []
    
    def add_point(self, strength=1000, location=(0, 0, 5), name="PointLight"):
        """Add a point light"""
        bpy.ops.object.light_add(type='POINT', location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = strength
        self.lights.append(light)
        return light
    
    def clear(self):
        """Remove all lights"""
        for light in self.lights:
            bpy.data.objects.remove(light, do_unlink=True)
        self.lights.clear()
```

**Usage:**
```python
renderables = RenderablesCollection()
lights = LightsCollection()

# Add objects
cube = renderables.add_cube(size=2.0, location=(0, 0, 0))
sphere = renderables.add_sphere(radius=1.5, location=(3, 0, 0))

# Add lights
lights.add_point(strength=1000, location=(5, 5, 5))
```

---

### 7. MCP Tool Definition

```python
# Source: blender-mcp/server.py:244-256

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BlenderMCP")

@mcp.tool()
def create_cube(size: float = 2.0, location: tuple = (0, 0, 0)) -> str:
    """
    Create a cube in the scene.
    
    Parameters:
    - size: Size of the cube
    - location: (x, y, z) position
    """
    try:
        def _create():
            bpy.ops.mesh.primitive_cube_add(size=size, location=location)
            return bpy.context.object.name
        
        # Execute in main thread
        result = {"name": None}
        def callback():
            result["name"] = _create()
            return None
        
        execute_in_main_thread(callback)
        
        # Wait for result (implement proper async handling in production)
        import time
        for _ in range(100):  # Wait up to 1 second
            if result["name"]:
                return f"Created cube: {result['name']}"
            time.sleep(0.01)
        
        return "Timeout creating cube"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

### 8. Feature Status Checking

```python
# Source: blender-mcp/server.py:527-542

@mcp.tool()
def get_capabilities() -> dict:
    """
    Get available capabilities and their status.
    Lets AI know what features are enabled.
    """
    return {
        "mesh_generation": True,
        "material_library": False,  # Not yet implemented
        "poly_haven": False,
        "rendering": True,
        "animation": False,
        "viewport_control": True,
    }

@mcp.tool()
def get_scene_info() -> str:
    """Get information about current scene"""
    info = {
        "name": bpy.context.scene.name,
        "objects": [obj.name for obj in bpy.data.objects],
        "cameras": [obj.name for obj in bpy.data.cameras],
        "lights": [obj.name for obj in bpy.data.lights],
    }
    return json.dumps(info, indent=2)
```

---

### 9. Command Handler Pattern

```python
# Pattern from blender-mcp/addon.py:192-252

class CommandRouter:
    """Route commands to appropriate handlers"""
    
    def __init__(self):
        self.handlers = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command handlers"""
        self.handlers = {
            "create_cube": self.create_cube,
            "create_sphere": self.create_sphere,
            "get_scene_info": self.get_scene_info,
        }
    
    def execute(self, command_type: str, params: dict):
        """Execute a command"""
        handler = self.handlers.get(command_type)
        if not handler:
            raise ValueError(f"Unknown command: {command_type}")
        
        return handler(**params)
    
    def create_cube(self, size=2.0, location=(0, 0, 0)):
        """Handler for create_cube command"""
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        return {"name": bpy.context.object.name}
    
    def create_sphere(self, radius=1.0, location=(0, 0, 0)):
        """Handler for create_sphere command"""
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
        return {"name": bpy.context.object.name}
    
    def get_scene_info(self):
        """Handler for get_scene_info command"""
        return {
            "objects": [obj.name for obj in bpy.data.objects],
            "cameras": [obj.name for obj in bpy.data.cameras],
        }
```

---

### 10. Complete MCP Server Template

```python
"""
Complete MCP server template for Blender sidecar
Combines patterns from blender-mcp and blendify
"""

import bpy
import json
from mcp.server.fastmcp import FastMCP
from typing import Optional

# ============================================================================
# Utilities
# ============================================================================

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

def execute_in_main_thread(callback):
    """Execute in Blender's main thread"""
    def wrapper():
        try:
            callback()
        except Exception as e:
            print(f"Error: {e}")
        return None
    bpy.app.timers.register(wrapper, first_interval=0.0)

# ============================================================================
# Scene Management
# ============================================================================

class Scene(metaclass=Singleton):
    """High-level scene management"""
    
    def __init__(self):
        self.renderables = RenderablesCollection()
        self.lights = LightsCollection()
        self._camera = None
    
    def clear(self):
        self.renderables.clear()
        self.lights.clear()
        if self._camera:
            bpy.data.objects.remove(self._camera, do_unlink=True)
            self._camera = None

class RenderablesCollection:
    def __init__(self):
        self.objects = []
    
    def add_cube(self, size=2.0, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = bpy.context.object
        self.objects.append(obj)
        return obj
    
    def clear(self):
        for obj in self.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.objects.clear()

class LightsCollection:
    def __init__(self):
        self.lights = []
    
    def add_point(self, strength=1000, location=(0, 0, 5)):
        bpy.ops.object.light_add(type='POINT', location=location)
        light = bpy.context.object
        light.data.energy = strength
        self.lights.append(light)
        return light
    
    def clear(self):
        for light in self.lights:
            bpy.data.objects.remove(light, do_unlink=True)
        self.lights.clear()

# ============================================================================
# MCP Server
# ============================================================================

mcp = FastMCP("BlenderSidecarMCP")
scene = Scene()

@mcp.tool()
def get_capabilities() -> str:
    """Get available capabilities"""
    caps = {
        "mesh_generation": True,
        "rendering": True,
        "scene_inspection": True,
    }
    return json.dumps(caps, indent=2)

@mcp.tool()
def create_cube(size: float = 2.0, x: float = 0, y: float = 0, z: float = 0) -> str:
    """
    Create a cube in the scene.
    
    Parameters:
    - size: Size of the cube
    - x, y, z: Position coordinates
    """
    result = {"name": None}
    
    def _create():
        obj = scene.renderables.add_cube(size=size, location=(x, y, z))
        result["name"] = obj.name
    
    execute_in_main_thread(_create)
    
    # Wait for result (implement proper async in production)
    import time
    for _ in range(100):
        if result["name"]:
            return f"Created cube: {result['name']}"
        time.sleep(0.01)
    
    return "Timeout"

@mcp.tool()
def get_scene_info() -> str:
    """Get current scene information"""
    info = {
        "objects": [obj.name for obj in bpy.data.objects],
        "cameras": len(bpy.data.cameras),
        "lights": len(bpy.data.lights),
    }
    return json.dumps(info, indent=2)

@mcp.tool()
def clear_scene() -> str:
    """Clear all objects from scene"""
    execute_in_main_thread(scene.clear)
    return "Scene cleared"

# ============================================================================
# Server Startup
# ============================================================================

def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
```

---

## Testing Snippets

### Test MCP Server Locally

```bash
# In terminal
cd /path/to/blender/sidecar
python mcp_server.py
```

### Test from Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender-sidecar": {
      "command": "/path/to/blender/python/bin/python",
      "args": ["/path/to/blender/sidecar/mcp_server.py"]
    }
  }
}
```

### Test Tool Execution

```python
# Test script
import json

# Simulate MCP tool call
result = create_cube(size=2.0, x=0, y=0, z=0)
print(result)

result = get_scene_info()
print(json.loads(result))
```

---

## Common Pitfalls

### ❌ DON'T: Execute bpy operations outside main thread
```python
# This will crash or behave unpredictably!
def bad_create_cube():
    import threading
    def create():
        bpy.ops.mesh.primitive_cube_add()  # WRONG!
    threading.Thread(target=create).start()
```

### ✅ DO: Use bpy.app.timers
```python
def good_create_cube():
    def create():
        bpy.ops.mesh.primitive_cube_add()
        return None
    bpy.app.timers.register(create, first_interval=0.0)
```

---

### ❌ DON'T: Create multiple server instances
```python
server1 = MCPServer()
server2 = MCPServer()  # BAD! Causes conflicts
```

### ✅ DO: Use singleton pattern
```python
class MCPServer(metaclass=Singleton):
    pass

server = MCPServer()  # OK
# server2 = MCPServer()  # Raises error
```

---

### ❌ DON'T: Ignore Blender's stdout spam
```python
bpy.ops.render.render()  # Prints tons of info
```

### ✅ DO: Suppress when appropriate
```python
with catch_stdout():
    bpy.ops.render.render()  # Silent
```

---

## Reference Links

- **Full Analysis:** [MCP_INTEGRATION_ANALYSIS.md](./MCP_INTEGRATION_ANALYSIS.md)
- **blender-mcp repo:** https://github.com/ahujasid/blender-mcp
- **blendify repo:** https://github.com/ptrvilya/blendify
- **MCP Protocol:** https://modelcontextprotocol.io/
- **FastMCP:** https://github.com/jlowin/fastmcp

---

**Last Updated:** October 5, 2025  
**Purpose:** Quick reference for implementation

