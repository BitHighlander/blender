# Redis Bridge Implementation Plan

**Goal**: Build a Redis Streams bridge that matches MCP socket server's flexibility  
**Approach**: Feature-for-feature parity with proven MCP architecture  
**Status**: Planning Phase  

---

## 🎯 Design Principles

### 1. Match MCP Capabilities
Every command available via MCP socket should work via Redis.

### 2. Keep What Works
- ✅ Background threading for Redis polling
- ✅ bpy.app.timers for command execution
- ✅ Simple JSON message format
- ✅ Comprehensive error handling

### 3. Add Redis Advantages
- ✨ Multiple workers (horizontal scaling)
- ✨ Persistent command queue
- ✨ Message acknowledgment
- ✨ Distributed tracing

---

## 📊 Architecture Comparison

### MCP Socket Server (Current - Working!)
```python
# scripts/startup/bl_mcp_server.py

class BlenderMCPServer:
    def start():
        # Background thread for socket I/O
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        
    def _handle_client(client):
        # Queue command for main thread
        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
    
    def execute_command(command):
        cmd_type = command.get("type")
        
        if cmd_type == "get_scene_info":
            return {"objects": len(bpy.data.objects), ...}
        elif cmd_type == "create_cube":
            bpy.ops.mesh.primitive_cube_add(...)
            return {"name": obj.name, ...}
```

**Commands Implemented**:
- `ping` - Health check
- `get_scene_info` - Scene statistics
- `create_cube` - Create cube geometry

---

### Redis Bridge (Target - To Build)

```python
# scripts/startup/bl_redis_bridge.py

class BlenderRedisBridge:
    def start():
        # Background thread for Redis polling
        self.consumer_thread = threading.Thread(target=self._consumer_loop, daemon=True)
        
    def _queue_command(message_id, command):
        # Queue command for main thread
        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
    
    def execute_command(command):
        cmd = command.get("cmd")  # Note: "cmd" not "type"
        params = command.get("params", {})
        
        if cmd == "GetSceneInfo":
            return {"objects": len(bpy.data.objects), ...}
        elif cmd == "CreateCube":
            bpy.ops.mesh.primitive_cube_add(...)
            return {"name": obj.name, ...}
```

**Command Format** (Redis):
```json
{
  "cmd": "CreateCube",
  "params": {"location": [0, 0, 2], "size": 1},
  "opts": {"reply_stream": "blender:reply"},
  "trace_id": "uuid",
  "span_id": "uuid"
}
```

**Response Format** (Redis):
```json
{
  "v": "1.0",
  "trace_id": "uuid",
  "span_id": "uuid",
  "status": "ok",
  "cmd": "CreateCube",
  "result": {"name": "Cube.001", "location": [0, 0, 2]},
  "metrics": {"cpu_ms": 15, "wall_ms": 23, ...}
}
```

---

## 🔨 Implementation Plan

### Phase 1: Core Bridge (Week 1)

**File**: `scripts/startup/bl_redis_bridge.py`

**Features**:
- [x] Background thread for Redis polling ✅ (Already done!)
- [x] bpy.app.timers command queueing ✅ (Already done!)
- [ ] Command routing (match MCP pattern)
- [ ] Error handling (match MCP pattern)
- [ ] Auto-start on Blender launch

**Commands to Port from MCP**:
- [ ] `Ping` → Mirror MCP `ping`
- [ ] `GetSceneInfo` → Mirror MCP `get_scene_info`
- [ ] `CreateCube` → Mirror MCP `create_cube`

**Success Criteria**:
- Redis bridge auto-starts with Blender
- Basic commands work
- No viewport freezing

---

### Phase 2: Blender API Coverage (Week 2)

**Goal**: Expose comprehensive Blender operations

#### Geometry Creation
- [ ] `CreateCube`, `CreateSphere`, `CreateCylinder`, `CreatePlane`
- [ ] `CreateMesh` - Custom mesh from vertices/faces
- [ ] `CreateCurve` - Bezier/NURBS curves
- [ ] `CreateText` - 3D text objects

#### Object Manipulation
- [ ] `TransformObject` - Move/rotate/scale
- [ ] `DeleteObject` - Remove objects
- [ ] `DuplicateObject` - Copy objects
- [ ] `JoinObjects` - Merge multiple objects
- [ ] `ParentObjects` - Set parent/child relationships

#### Material & Shading
- [ ] `CreateMaterial` - New material
- [ ] `AssignMaterial` - Apply to object
- [ ] `SetShaderNode` - Node-based shading
- [ ] `SetColor` - Simple object color

#### Scene Management
- [ ] `GetSceneInfo` - Full scene data
- [ ] `GetObjectList` - List all objects
- [ ] `GetObjectInfo` - Detailed object data
- [ ] `SetCamera` - Camera operations
- [ ] `SetLighting` - Light operations

#### Animation
- [ ] `SetKeyframe` - Add keyframe
- [ ] `CreateAnimation` - Keyframe sequence
- [ ] `SetAnimationRange` - Timeline settings

#### Modifiers
- [ ] `AddModifier` - Subdivision, bevel, etc.
- [ ] `ApplyModifier` - Bake modifier
- [ ] `RemoveModifier` - Delete modifier

#### Rendering
- [ ] `SetRenderSettings` - Resolution, samples, etc.
- [ ] `RenderFrame` - Render current frame
- [ ] `RenderAnimation` - Render sequence

#### Import/Export
- [ ] `ImportFBX`, `ImportOBJ`, `ImportGLTF`
- [ ] `ExportFBX`, `ExportOBJ`, `ExportGLTF`
- [ ] `SaveBlendFile` - Save .blend
- [ ] `LoadBlendFile` - Load .blend

---

### Phase 3: Advanced Features (Week 3)

#### Python Execution
- [ ] `ExecutePython` - Run arbitrary Python in Blender
  - **Security**: Sandbox/whitelist only safe operations
  - **Use case**: Complex operations not exposed as commands

#### Batch Operations
- [ ] `BatchCommands` - Execute multiple commands in one call
- [ ] Transaction support (all-or-nothing)

#### Asset Library
- [ ] `LoadAsset` - From asset library
- [ ] `SaveAsset` - To asset library
- [ ] `SearchAssets` - Query available assets

#### Geometry Nodes
- [ ] `CreateGeometryNode` - Node-based modeling
- [ ] `SetNodeParameter` - Configure nodes
- [ ] `ApplyGeometryNodes` - Execute node tree

---

## 📋 Command Registry Pattern

### MCP Pattern (Simple, Works)

```python
def execute_command(self, command):
    cmd_type = command.get("type")
    params = command.get("params", {})
    
    if cmd_type == "ping":
        return {"pong": True, ...}
    elif cmd_type == "create_cube":
        return self._create_cube(params)
    # ... more commands
```

**Pros**: 
- Simple
- Easy to understand
- Works perfectly

**Cons**:
- if/elif chain gets long
- Hard to auto-document
- No type checking

---

### Redis Bridge Pattern (Better for 100+ commands)

```python
class CommandRegistry:
    def __init__(self):
        self.handlers = {
            "Ping": self._handle_ping,
            "GetSceneInfo": self._handle_scene_info,
            "CreateCube": self._handle_create_cube,
            # ... auto-discovered from decorators
        }
    
    @register_command("Ping")
    def _handle_ping(self, params):
        return {"pong": True}
    
    @register_command("CreateCube", params_schema={...})
    def _handle_create_cube(self, params):
        location = params.get("location", [0, 0, 0])
        bpy.ops.mesh.primitive_cube_add(location=location)
        return {"name": obj.name}
```

**Pros**:
- Scalable to hundreds of commands
- Auto-documentation from decorators
- Type checking possible
- Easy to test individual commands

---

## 🗺️ File Structure

```
blender/
├── scripts/
│   ├── startup/
│   │   ├── bl_mcp_server.py          ✅ MCP socket (working!)
│   │   └── bl_redis_bridge.py        ⏳ Redis bridge (to build)
│   └── modules/
│       ├── sidecar/                  ✅ Existing (needs cleanup)
│       │   ├── consumer.py           - Has threading fix
│       │   ├── router.py             - Simple registry
│       │   └── commands/
│       │       ├── ping.py
│       │       ├── mesh.py
│       │       └── [add more].py
│       └── blender_bridge/           ⏳ New shared library
│           ├── command_registry.py   - Decorator-based registry
│           ├── geometry.py           - Geometry operations
│           ├── materials.py          - Material operations
│           ├── animation.py          - Animation helpers
│           └── utils.py              - Common utilities
```

---

## 🚀 Implementation Steps

### Step 1: Refactor MCP Server to Use Registry

Extract command handlers:
```python
# scripts/startup/bl_mcp_server.py
from blender_bridge.command_registry import CommandRegistry

class BlenderMCPServer:
    def __init__(self):
        self.registry = CommandRegistry()
    
    def execute_command(self, command):
        return self.registry.execute(
            cmd_type=command.get("type"),
            params=command.get("params", {})
        )
```

### Step 2: Create Redis Bridge Using Same Registry

```python
# scripts/startup/bl_redis_bridge.py
from blender_bridge.command_registry import CommandRegistry  # SAME!

class BlenderRedisBridge:
    def __init__(self):
        self.registry = CommandRegistry()  # SHARED code!
    
    def execute_command(self, command):
        return self.registry.execute(
            cmd_type=command.get("cmd"),
            params=command.get("params", {})
        )
```

### Step 3: Add Commands to Shared Registry

```python
# scripts/modules/blender_bridge/command_registry.py

@register_command("GetSceneInfo")
def get_scene_info(params):
    return {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        ...
    }

@register_command("CreateCube")  
def create_cube(params):
    location = params.get("location", [0, 0, 0])
    size = params.get("size", 2)
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.view_layer.objects.active or bpy.context.scene.objects[-1]
    return {"name": obj.name, "location": list(obj.location)}
```

**Result**: Both MCP and Redis get ALL commands automatically!

---

## 📦 Separate Control Project

### Project Structure
```
blender-control/              # New repo
├── package.json
├── src/
│   ├── mcp_client.ts         # MCP socket client
│   ├── redis_client.ts       # Redis streams client
│   ├── blender_api.ts        # Unified API (uses either backend)
│   └── commands/
│       ├── geometry.ts       # Geometry command builders
│       ├── materials.ts      # Material command builders
│       ├── animation.ts      # Animation command builders
│       └── scene.ts          # Scene command builders
├── examples/
│   ├── create_room.ts        # Example: Create a room
│   ├── animate_camera.ts     # Example: Camera animation
│   └── procedural_city.ts    # Example: Generate city
└── README.md
```

### Unified API Example

```typescript
// Use either MCP or Redis - same API!
import { BlenderAPI } from './blender_api';

const blender = new BlenderAPI({
  backend: 'mcp',  // or 'redis'
  connection: { host: 'localhost', port: 9876 }
});

await blender.connect();

// Same commands work with both backends
const cube = await blender.createCube({ location: [0, 0, 2], size: 1 });
const scene = await blender.getSceneInfo();
await blender.createMaterial({ name: 'Metal', metallic: 1.0 });
```

---

## 🎬 Next Actions

### Immediate (Today/Tomorrow)
1. ✅ **Document what we learned** (this file!)
2. ✅ **MCP server working** (done!)
3. [ ] **Clean up sidecar code** (remove dungeon stuff)
4. [ ] **Create command registry system**

### Short Term (This Week)
1. [ ] **Port 10-15 core commands** from blender-mcp addon.py
2. [ ] **Test each command** via both MCP and Redis
3. [ ] **Document API** (OpenAPI/JSON Schema)
4. [ ] **Create TypeScript client library**

### Medium Term (Next Week)
1. [ ] **Cover 80% of common Blender operations**
2. [ ] **Add batching support**
3. [ ] **Performance optimization**
4. [ ] **Full integration tests**

### Long Term (Month 1)
1. [ ] **Separate control project** (`blender-control` npm package)
2. [ ] **Cursor agent integration**
3. [ ] **Documentation site**
4. [ ] **Example projects**

---

## 📝 Command Inventory

### From blender-mcp addon.py

Review `.analysis/blender-mcp/addon.py` to extract all commands:

**Scene Operations**:
- get_scene_info
- execute_python
- undo/redo

**Object Operations**:
- create primitives (cube, sphere, cylinder, etc)
- transform_object
- delete_object
- select_object

**Mesh Operations**:
- edit_mesh
- apply_modifier
- subdivide

**Material/Rendering**:
- create_material
- set_material_color
- render_image

**Camera/View**:
- set_camera_location
- set_camera_rotation
- look_at

**Asset Integration**:
- download_polyhaven_hdri
- download_polyhaven_texture
- import_3d_model (Rodin, Hypersim, Sketchfab)

**Full list**: See `.analysis/blender-mcp/addon.py` lines 182-1659

---

## 🏗️ Build System Integration

### How to Add Commands

1. **Add to shared registry**:
   ```python
   # scripts/modules/blender_bridge/commands/geometry.py
   
   @register_command("CreateSphere")
   def create_sphere(params):
       radius = params.get("radius", 1)
       location = params.get("location", [0, 0, 0])
       bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
       obj = bpy.context.view_layer.objects.active
       return {"name": obj.name, "location": list(obj.location)}
   ```

2. **Rebuild Blender**:
   ```bash
   make developer ninja  # 3-4 seconds
   ```

3. **Test via MCP**:
   ```javascript
   // Node.js
   client.write(JSON.stringify({
     type: "CreateSphere",
     params: { radius: 2, location: [0, 0, 5] }
   }));
   ```

4. **Test via Redis**:
   ```bash
   redis-cli XADD blender:cmd "*" payload '{
     "cmd": "CreateSphere",
     "params": {"radius": 2, "location": [0, 0, 5]}
   }'
   ```

**Same code, two protocols!**

---

## 📐 API Design

### Command Naming Convention

**MCP**: lowercase_with_underscores (Python style)
- `get_scene_info`
- `create_cube`
- `set_material_color`

**Redis**: PascalCase (match existing sidecar)
- `GetSceneInfo`
- `CreateCube`
- `SetMaterialColor`

**Solution**: Registry supports BOTH!
```python
@register_command("CreateCube", aliases=["create_cube"])
def create_cube(params):
    ...
```

### Parameter Validation

```python
from typing import TypedDict, Optional

class CreateCubeParams(TypedDict):
    location: Optional[list[float]]  # [x, y, z]
    size: Optional[float]
    name: Optional[str]

@register_command("CreateCube", params_schema=CreateCubeParams)
def create_cube(params: CreateCubeParams):
    # Auto-validated!
    location = params.get("location", [0, 0, 0])
    ...
```

---

## 🧪 Testing Strategy

### Unit Tests (Per Command)

```python
# tests/test_commands.py

def test_create_cube():
    result = create_cube({"location": [1, 2, 3], "size": 2})
    assert result["status"] == "success"
    assert result["result"]["location"] == [1, 2, 3]
```

### Integration Tests (End-to-End)

```javascript
// test/integration/mcp_redis_parity.test.mjs

test('CreateCube works same via MCP and Redis', async () => {
  const mcpResult = await mcpClient.send({ type: 'create_cube', ... });
  const redisResult = await redisClient.send({ cmd: 'CreateCube', ... });
  
  expect(mcpResult).toEqual(redisResult);
});
```

### Performance Tests

```javascript
test('100 cubes in < 5 seconds', async () => {
  const start = Date.now();
  
  for (let i = 0; i < 100; i++) {
    await blender.createCube({ location: [i, 0, 0] });
  }
  
  const elapsed = Date.now() - start;
  expect(elapsed).toBeLessThan(5000);
});
```

---

## 📚 Documentation Plan

### 1. API Reference (Auto-Generated)

```bash
# Generate from decorators
python scripts/generate_api_docs.py > API_REFERENCE.md
```

### 2. OpenAPI Spec

```yaml
openapi: 3.0.0
info:
  title: Blender Bridge API
  version: 2.0.0-realtime

paths:
  /CreateCube:
    post:
      parameters:
        - name: location
          schema:
            type: array
            items: { type: number }
```

### 3. TypeScript Definitions

```typescript
// blender-api.d.ts

export interface CreateCubeParams {
  location?: [number, number, number];
  size?: number;
  name?: string;
}

export interface CreateCubeResult {
  name: string;
  location: [number, number, number];
}

export class BlenderAPI {
  createCube(params: CreateCubeParams): Promise<CreateCubeResult>;
  getSceneInfo(): Promise<SceneInfo>;
  // ... all commands
}
```

---

## 🔧 Current Code Status

### What We Have (Working)

**MCP Socket Server**:
- File: `scripts/startup/bl_mcp_server.py`
- Status: ✅ **WORKING** (tested, verified!)
- Commands: 3 (ping, get_scene_info, create_cube)
- Integration: First-class (auto-starts)

**Redis Sidecar**:
- Files: `sidecar/*.py`
- Status: ✅ Threading fixed, ⚠️ needs cleanup
- Commands: 6 (Ping, CreateCube, CreateRoom, + 3 dungeon - to remove)
- Integration: Manual start (`--python sidecar.py`)

### What Needs Cleanup

1. **Remove dungeon commands** from sidecar
   - `sidecar/commands/dungeon.py` → DELETE
   - `sidecar/commands/dungeon_simple.py` → DELETE
   - Keep only: ping, mesh (CreateCube, CreateRoom)

2. **Unify command patterns**
   - Extract handlers to `blender_bridge/`
   - Share between MCP and Redis
   - Use decorator registry

3. **Fix sidecar auto-start**
   - Move to `scripts/startup/bl_redis_bridge.py`
   - Make it first-class like MCP
   - No manual `--python sidecar.py` needed

---

## 🎯 Success Criteria

### Phase 1 Done When:
- [ ] Both MCP and Redis auto-start with Blender
- [ ] Same 10 core commands work on both
- [ ] Test scripts pass for both protocols
- [ ] No viewport freezing
- [ ] No crashes

### Full Project Done When:
- [ ] 50+ Blender operations exposed
- [ ] TypeScript client library published
- [ ] Cursor agent can control Blender via MCP
- [ ] Separate control project (`blender-control`) exists
- [ ] Documentation complete
- [ ] Example projects demonstrating usage

---

## 💡 Key Insight

**Both protocols use the SAME underlying code!**

```
┌─────────┐         ┌──────────┐
│   MCP   │────┐    │  Redis   │────┐
└─────────┘    │    └──────────┘    │
               ▼                     ▼
         ┌──────────────────────────────┐
         │  Shared Command Registry     │
         │  (blender_bridge/*)          │
         │                              │
         │  - create_cube()             │
         │  - get_scene_info()          │
         │  - All Blender operations    │
         └───────────┬──────────────────┘
                     │
              ┌──────▼──────┐
              │ Blender bpy │
              └─────────────┘
```

**Write the command once, works in both!**

---

## 📖 References

- **blender-mcp**: https://github.com/ahujasid/blender-mcp
- **MCP Protocol**: https://modelcontextprotocol.io
- **Blender Python API**: https://docs.blender.org/api/current/
- **Your fork**: https://github.com/BitHighlander/blender (master-degen)

---

**Ready to build the Redis bridge with feature parity!** 🚀

