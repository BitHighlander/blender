# MCP Integration Analysis & Architecture

**Status:** Research & Planning  
**Date:** October 2025  
**Purpose:** Document analysis of existing Blender MCP integrations and define architecture for first-class integration

---

## Table of Contents

1. [Overview](#overview)
2. [Reference Projects](#reference-projects)
3. [Architectural Comparison](#architectural-comparison)
4. [Key Insights](#key-insights)
5. [Recommended Architecture](#recommended-architecture)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Code References](#code-references)

---

## Overview

This document analyzes two different approaches to integrating Blender with AI systems and derives best practices for our **first-class MCP integration** within the Blender sidecar.

**Goal:** Create a native MCP (Model Context Protocol) integration that:
- Runs as part of Blender's core process (not a plugin)
- Uses the existing sidecar architecture
- Provides high-level, semantic API for AI agents
- Eliminates IPC overhead where possible
- Respects Blender's threading model

---

## Reference Projects

### 1. **blender-mcp** (Plugin Approach)

**Repository:** https://github.com/ahujasid/blender-mcp  
**License:** MIT  
**Stars:** 13.7k (as of Oct 2025)  

**Description:** External MCP server that communicates with Blender via TCP sockets through a plugin addon.

**Key Files to Study:**
- [`addon.py`](https://github.com/ahujasid/blender-mcp/blob/main/addon.py) - Blender addon with socket server
- [`src/blender_mcp/server.py`](https://github.com/ahujasid/blender-mcp/blob/main/src/blender_mcp/server.py) - MCP server implementation

**Architecture:**
```
┌──────────────┐         TCP Socket          ┌──────────────┐
│   Claude AI  │ ←────── (Port 9876) ──────→ │   Blender    │
└──────────────┘                              │   + Addon    │
       ↓                                      └──────────────┘
┌──────────────┐
│ MCP Server   │
│ (External)   │
└──────────────┘
```

### 2. **blendify** (Library Approach)

**Repository:** https://github.com/ptrvilya/blendify  
**License:** GPL v3  
**Paper:** [arXiv:2410.17858](https://arxiv.org/abs/2410.17858)  

**Description:** Python framework providing high-level API for programmatic Blender rendering, primarily for computer vision and ML workflows.

**Key Files to Study:**
- [`blendify/scene.py`](https://github.com/ptrvilya/blendify/blob/main/blendify/scene.py) - Main Scene class with singleton pattern
- [`blendify/__init__.py`](https://github.com/ptrvilya/blendify/blob/main/blendify/__init__.py) - Module initialization and exit handling
- [`blendify/internal/singleton.py`](https://github.com/ptrvilya/blendify/blob/main/blendify/internal/singleton.py) - Singleton metaclass
- [`blendify/internal/execution_decorator.py`](https://github.com/ptrvilya/blendify/blob/main/blendify/internal/execution_decorator.py) - Safe exit decorator
- [`blendify/renderables/primitives.py`](https://github.com/ptrvilya/blendify/blob/main/blendify/renderables/primitives.py) - High-level mesh primitives
- [`examples/01_cornell_box.py`](https://github.com/ptrvilya/blendify/blob/main/examples/01_cornell_box.py) - Example usage

**Architecture:**
```
┌──────────────────┐
│  Python Script   │
│  import blendify │
└────────┬─────────┘
         │ Direct API calls
         ↓
┌──────────────────┐
│  blendify lib    │
│  └→ bpy module   │
│     └→ Blender   │
└──────────────────┘
```

---

## Architectural Comparison

### blender-mcp (Plugin/External)

#### Strengths
✅ **Universal compatibility** - Works with any Blender installation  
✅ **Runtime control** - Start/stop server from UI  
✅ **Feature toggles** - Conditionally enable integrations (PolyHaven, Hyper3D, Sketchfab)  
✅ **Thread safety** - Uses `bpy.app.timers.register()` for main thread execution  
✅ **Reconnection logic** - Handles dropped connections gracefully  
✅ **Production ready** - 13k+ users, battle-tested  

#### Limitations
❌ **Socket overhead** - Network roundtrip for every command (~ms latency)  
❌ **Addon restrictions** - Limited to Blender Python API surface  
❌ **Manual installation** - Users must install addon manually  
❌ **Process boundary** - All data must be serialized to JSON  
❌ **Port conflicts** - Requires managing TCP port 9876  

#### Key Technical Patterns

**1. Thread-Safe Command Execution:**
```python
# From: addon.py, line 144-166
def execute_wrapper():
    try:
        response = self.execute_command(command)
        response_json = json.dumps(response)
        client.sendall(response_json.encode('utf-8'))
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        error_response = {"status": "error", "message": str(e)}
        client.sendall(json.dumps(error_response).encode('utf-8'))
    return None

# Schedule execution in main thread - CRITICAL!
bpy.app.timers.register(execute_wrapper, first_interval=0.0)
```

**2. Feature Status Checking:**
```python
# From: addon.py, line 197-220
if cmd_type == "get_polyhaven_status":
    return {"status": "success", "result": self.get_polyhaven_status()}

handlers = {
    "get_scene_info": self.get_scene_info,
    "execute_code": self.execute_code,
}

# Add handlers only if feature enabled
if bpy.context.scene.blendermcp_use_polyhaven:
    polyhaven_handlers = {
        "get_polyhaven_categories": self.get_polyhaven_categories,
        "search_polyhaven_assets": self.search_polyhaven_assets,
    }
    handlers.update(polyhaven_handlers)
```

**3. JSON Command Protocol:**
```python
# Command format
{
    "type": "get_scene_info",
    "params": {}
}

# Response format
{
    "status": "success",
    "result": {
        "name": "Scene",
        "objects": [...]
    }
}
```

---

### blendify (Library/Embedded)

#### Strengths
✅ **Zero IPC overhead** - Direct function calls  
✅ **Pythonic API** - Clean, high-level abstractions  
✅ **Works in notebooks** - Google Colab compatible  
✅ **Batch rendering** - Optimized for ML/CV workflows  
✅ **Clean abstractions** - Hides Blender complexity  
✅ **Academic pedigree** - Used in multiple CVPR/ECCV papers  

#### Limitations
❌ **No interactive mode** - Designed for scripting, not UI  
❌ **Requires `bpy` module** - Can't run in standard Python  
❌ **Headless focus** - Not designed for real-time viewport work  
❌ **Academic focus** - Optimized for specific CV/ML use cases  

#### Key Technical Patterns

**1. Singleton Scene Pattern:**
```python
# From: scene.py, line 27-34
class Scene(metaclass=Singleton):
    def __init__(self):
        self.renderables = RenderablesCollection()
        self.lights = LightsCollection()
        self._camera = None
        self._reset_scene()
```

```python
# From: internal/singleton.py
class Singleton(type):
    """Only one instance of the class allowed"""
    _instances = dict()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]
        else:
            raise RuntimeError(f"Only one instance of class {cls.__name__} is allowed")
```

**2. Safe Exit Decorator:**
```python
# From: internal/execution_decorator.py
_bpy_exit_bypassed = False

def safe_exit(func):
    """Catches exceptions and prevents Blender memory leak detection hang"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            global _bpy_exit_bypassed
            _bpy_exit_bypassed = True
            print(f"blendify caught error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
    return wrapper
```

**3. High-Level Semantic API:**
```python
# From: examples/01_cornell_box.py
from blendify import scene
from blendify.materials import PrincipledBSDFMaterial
from blendify.colors import UniformColors

# Simple, declarative API
scene.lights.add_point(strength=1000, translation=(4, -2, 4))
scene.set_perspective_camera((512, 512), fov_x=0.7)

material = PrincipledBSDFMaterial()
color = UniformColors((0.0, 1.0, 0.0))
scene.renderables.add_cube_mesh(1.0, material, color)

scene.render(filepath="output.png")
```

**4. Context Manager for Output Control:**
```python
# From: internal/io.py (referenced in scene.py)
with catch_stdout(skip=verbose):
    bpy.ops.render.render(write_still=False)
```

**5. Collections Pattern:**
```python
# Organized grouping of related objects
scene.renderables  # RenderablesCollection
scene.lights       # LightsCollection
scene.camera       # Camera instance
```

---

## Key Insights

### Critical Lessons for First-Class Integration

#### 1. Threading is Non-Negotiable
```python
# ALWAYS use bpy.app.timers for main thread execution
# Source: blender-mcp/addon.py:166
bpy.app.timers.register(callback, first_interval=0.0)
```

**Why:** Blender's UI and core operations must run on the main thread. Any external integration must respect this.

**Implementation Note:** Our sidecar already has threading considerations (see `docs/sidecar/THREADING.md`). We need to ensure MCP tools use the same pattern.

---

#### 2. Singleton for Server Management
```python
# Source: blendify/internal/singleton.py
class MCPServer(metaclass=Singleton):
    """Only one MCP server instance should exist"""
```

**Why:** Prevents multiple server instances competing for resources.

**Implementation Note:** The sidecar router should be refactored to use singleton pattern.

---

#### 3. High-Level Abstractions Over Raw API
```python
# BAD: Exposing raw bpy
mcp.tool("execute_python")(lambda code: exec(code))

# GOOD: Semantic operations
mcp.tool("create_room")(lambda width, depth, height: 
    create_dungeon_room(width, depth, height))
```

**Reference:** See blendify's semantic API in `renderables/primitives.py`

**Why:** AI agents work better with human-like abstractions than low-level API calls.

---

#### 4. Feature Status Checking
```python
# Source: blender-mcp/server.py:527-542
@mcp.tool()
def get_polyhaven_status() -> str:
    """Check if PolyHaven integration is enabled"""
    blender = get_blender_connection()
    result = blender.send_command("get_polyhaven_status")
    return result.get("message", "")
```

**Why:** Let AI know what's available before attempting to use it.

**Implementation Note:** We should add status tools for:
- Mesh generation capabilities
- Available material libraries
- Rendering options
- Asset import/export formats

---

#### 5. Safe Exit Handling
```python
# Source: blendify/internal/execution_decorator.py
@safe_exit
def render():
    """Prevents Blender memory leak detection from hanging process"""
```

**Why:** Blender has memory leak detection that can cause hangs on exit. Handle gracefully.

---

#### 6. Stdout/Stderr Control
```python
# Source: blendify (pattern used throughout)
with catch_stdout(skip=verbose):
    bpy.ops.render.render()
```

**Why:** Blender can be very chatty. Control when output is visible.

---

## Recommended Architecture

### Hybrid Approach: Best of Both Worlds

```
┌─────────────────────────────────────────────────────────────┐
│                     Blender (C++ Core)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Python Interpreter (bpy module)             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Sidecar Process                     │  │  │
│  │  │                                                  │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │         MCP Server (FastMCP/Stdio)        │ │  │  │
│  │  │  │  - Native to Blender process              │ │  │  │
│  │  │  │  - No socket overhead                     │ │  │  │
│  │  │  │  - Singleton instance                     │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  │                      ↓                           │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │    High-Level Semantic API Layer          │ │  │  │
│  │  │  │  (Inspired by blendify)                   │ │  │  │
│  │  │  │                                            │ │  │  │
│  │  │  │  • DungeonGenerator                       │ │  │  │
│  │  │  │  • MaterialLibrary                        │ │  │  │
│  │  │  │  • SceneInspector                         │ │  │  │
│  │  │  │  • MeshOperations                         │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  │                      ↓                           │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │       Thread Bridge Layer                 │ │  │  │
│  │  │  │  (bpy.app.timers for main thread)         │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  │                      ↓                           │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │         Command Router                    │ │  │  │
│  │  │  │  (Existing sidecar/router.py)             │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  │                      ↓                           │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │    Command Handlers                       │ │  │  │
│  │  │  │  (Existing sidecar/commands/)             │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  │                      ↓                           │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │         Blender Python API (bpy)          │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ stdio (MCP)
                           │
                    ┌──────────────┐
                    │  AI Client   │
                    │  (Claude,    │
                    │   Cursor)    │
                    └──────────────┘
```

### Architecture Benefits

1. ✅ **No socket overhead** - Direct function calls (like blendify)
2. ✅ **Thread-safe** - Uses `bpy.app.timers` (like blender-mcp)
3. ✅ **High-level API** - Semantic operations (like blendify)
4. ✅ **Built into Blender** - First-class integration (unique!)
5. ✅ **Feature toggles** - Conditional capabilities (like blender-mcp)
6. ✅ **Existing infrastructure** - Leverages sidecar router and commands

---

## Implementation Roadmap

### Phase 1: MCP Server Foundation
**Goal:** Basic MCP server running within sidecar

**Tasks:**
- [ ] Add FastMCP dependency to `requirements.txt`
- [ ] Create `sidecar/mcp_server.py` with singleton pattern
- [ ] Implement basic stdio-based MCP server
- [ ] Add thread bridge using `bpy.app.timers`
- [ ] Create safe exit handler (blendify pattern)

**Reference Code:**
- blender-mcp: `server.py:167-201` (lifespan management)
- blendify: `internal/execution_decorator.py` (safe exit)

---

### Phase 2: High-Level Semantic API
**Goal:** Create blendify-style abstractions for common operations

**Tasks:**
- [ ] Create `sidecar/api/` module structure
- [ ] Implement `DungeonGenerator` class
- [ ] Implement `SceneInspector` class  
- [ ] Implement `MaterialLibrary` class
- [ ] Add collections pattern (renderables, lights, etc.)

**Reference Code:**
- blendify: `scene.py` (Scene class structure)
- blendify: `renderables/primitives.py` (high-level primitives)
- blendify: `materials/` (material abstractions)

---

### Phase 3: MCP Tools
**Goal:** Expose semantic API as MCP tools

**Tasks:**
- [ ] `create_dungeon_room` tool
- [ ] `create_dungeon_corridor` tool
- [ ] `inspect_scene` tool
- [ ] `apply_material` tool
- [ ] `get_capabilities` tool (feature status)

**Reference Code:**
- blender-mcp: `server.py:244-256` (tool definitions)
- blender-mcp: `server.py:527-542` (status checking)

---

### Phase 4: Integration Testing
**Goal:** Verify MCP integration with AI clients

**Tasks:**
- [ ] Test with Claude Desktop
- [ ] Test with Cursor
- [ ] Benchmark latency vs socket approach
- [ ] Document AI usage patterns
- [ ] Create example prompts

---

### Phase 5: Advanced Features
**Goal:** Add sophisticated capabilities

**Tasks:**
- [ ] Asset library integration (PolyHaven-style)
- [ ] Procedural generation tools
- [ ] Viewport screenshot capture
- [ ] Animation timeline control
- [ ] Material node manipulation

**Reference Code:**
- blender-mcp: `addon.py:424-790` (PolyHaven integration)
- blender-mcp: `server.py:275-315` (viewport screenshots)

---

## Code References

### Must-Read Code Sections

#### From blender-mcp:

1. **Thread-safe execution:**
   - File: `addon.py`
   - Lines: 144-180
   - Pattern: `bpy.app.timers.register()`

2. **Feature-based handlers:**
   - File: `addon.py`
   - Lines: 192-252
   - Pattern: Conditional handler registration

3. **MCP tool definitions:**
   - File: `server.py`
   - Lines: 244-525
   - Pattern: FastMCP tool decorators

4. **Persistent connection management:**
   - File: `server.py`
   - Lines: 209-241
   - Pattern: Global connection with reconnection logic

#### From blendify:

1. **Singleton pattern:**
   - File: `internal/singleton.py`
   - Lines: 1-14
   - Pattern: Metaclass singleton

2. **Safe exit handling:**
   - File: `internal/execution_decorator.py`
   - Lines: 1-26
   - Pattern: Exception decorator

3. **Scene management:**
   - File: `scene.py`
   - Lines: 27-84
   - Pattern: Singleton scene with collections

4. **High-level primitives:**
   - File: `renderables/primitives.py`
   - Lines: 98-148
   - Pattern: Semantic mesh operations

5. **Clean API example:**
   - File: `examples/01_cornell_box.py`
   - Lines: 10-79
   - Pattern: Declarative scene construction

---

## Directory Structure Proposal

```
sidecar/
├── __init__.py
├── mcp_server.py              # Main MCP server (singleton)
├── router.py                  # Existing command router
├── commands/                  # Existing command handlers
│   └── mesh.py
├── mcp/                       # NEW: MCP-specific code
│   ├── __init__.py
│   ├── tools.py               # MCP tool definitions
│   ├── decorators.py          # safe_exit, thread_safe, etc.
│   └── capabilities.py        # Feature status checking
├── api/                       # NEW: High-level semantic API
│   ├── __init__.py
│   ├── dungeon.py            # DungeonGenerator
│   ├── scene.py              # SceneInspector
│   ├── materials.py          # MaterialLibrary
│   ├── renderables.py        # RenderablesCollection (blendify-style)
│   └── lights.py             # LightsCollection (blendify-style)
└── internal/                  # NEW: Internal utilities
    ├── __init__.py
    ├── singleton.py           # Singleton metaclass (from blendify)
    ├── threading.py           # bpy.app.timers wrapper
    └── io.py                  # stdout/stderr control
```

---

## Related Documents

- [THREADING.md](./THREADING.md) - Threading model and safety
- [MILESTONE_1_PLAN.md](./MILESTONE_1_PLAN.md) - Current dungeon mesh milestone
- [SPEC.md](./SPEC.md) - Sidecar specification
- [ROADMAP.md](./ROADMAP.md) - Development roadmap

---

## External Resources

### blender-mcp
- **GitHub:** https://github.com/ahujasid/blender-mcp
- **Documentation:** See README.md in repository
- **Key Learning:** Thread safety, feature toggles, MCP server patterns

### blendify
- **GitHub:** https://github.com/ptrvilya/blendify
- **Documentation:** https://virtualhumans.mpi-inf.mpg.de/blendify/
- **Paper:** https://arxiv.org/abs/2410.17858
- **Google Colab Demo:** https://colab.research.google.com/github/ptrvilya/blendify/blob/main/examples/ipynb/blendify_colab_demo.ipynb
- **Key Learning:** High-level API design, singleton pattern, safe exit handling

### MCP Protocol
- **Specification:** https://modelcontextprotocol.io/
- **FastMCP:** https://github.com/jlowin/fastmcp

---

## Next Steps

1. **Review this document** with the team
2. **Prioritize Phase 1** tasks in next sprint
3. **Prototype MCP server** integration in sidecar
4. **Benchmark** latency improvements over socket approach
5. **Design semantic API** for dungeon generation (our use case)

---

## Notes

- This is a **living document** - update as we learn from implementation
- Code references are accurate as of Oct 2025 - verify line numbers if repositories update
- Focus on **incremental delivery** - start simple, add complexity as needed
- Both reference projects are open source - we can learn freely but must respect licenses
  - blender-mcp: MIT (permissive)
  - blendify: GPL v3 (copyleft - be cautious with code reuse)

---

**Last Updated:** October 5, 2025  
**Author:** Development Team  
**Status:** Research Complete → Ready for Implementation

