# 🏰 Dungeon Generation Learning Journal

**Goal**: Document the learning process of building a dungeon generation system using Blender + Redis Bridge.

**Status**: Active Development  
**Start Date**: October 5, 2025  
**Project**: Degenerate Labs - Blender Redis Bridge  

---

## 🎯 Project Overview

### What We're Building

A **procedural dungeon generation system** that demonstrates:
1. Redis Streams bridge for Blender automation
2. High-level orchestrator (Node.js) for game logic
3. Low-level Blender sidecar for mesh operations
4. Real-time, non-blocking command execution
5. Complete dungeon generation workflow

### Architecture

```
┌──────────────────────┐         ┌─────────┐         ┌──────────────────┐
│   Orchestrator       │ XADD    │  Redis  │ XREAD   │   Blender        │
│    (Node.js)         ├────────>│ Streams │<────────┤   Sidecar        │
│                      │         │         │         │   (Python)       │
│  - Dungeon Logic     │<────────┤         ├────────>│ - Mesh Ops       │
│  - Room Layout       │  XREAD  │  CMD    │  XADD   │ - bpy.app.timers │
│  - Pathfinding       │         │  REPLY  │         │ - Threading      │
└──────────────────────┘         └─────────┘         └──────────────────┘
```

**Why This Split?**
- **Orchestrator** = Brain (game logic, algorithms, rules)
- **Blender Sidecar** = Hands (3D operations, mesh creation, export)

This keeps Blender commands **simple, reusable primitives** while all complexity lives in the orchestrator.

---

## 📚 Directory Structure

```
blender/
├── orchestrator/              # NEW: Node.js dungeon generation orchestrator
│   ├── src/
│   │   ├── lib/
│   │   │   └── blender-client.js      # Redis client for Blender
│   │   ├── commands/                   # High-level command builders
│   │   ├── dungeon/                    # Dungeon generation algorithms
│   │   │   ├── generator.js           # Main dungeon generator
│   │   │   ├── room-placer.js         # Room placement logic
│   │   │   └── corridor-router.js     # Corridor pathfinding
│   │   └── examples/                   # Test scripts
│   │       ├── test-ping.js           # Connection test
│   │       ├── test-cube.js           # Single cube
│   │       └── test-room.js           # Single room
│   ├── package.json
│   └── README.md
│
├── sidecar/                   # Python Redis consumer (Blender side)
│   ├── __init__.py           # Version: 2.0.0-realtime
│   ├── consumer.py           # Background thread + bpy.app.timers
│   ├── router.py             # Command routing
│   └── commands/             # Command handlers
│       ├── ping.py
│       ├── mesh.py           # CreateCube, CreateRoom
│       └── dungeon.py        # Dungeon-specific commands
│
├── scripts/startup/          # Auto-start on Blender launch
│   ├── bl_mcp_server.py     # MCP socket server (port 9876)
│   └── bl_redis_bridge.py   # (Future) Redis bridge startup
│
├── test_dungeon.mjs          # Test: Full dungeon generation
├── test_mcp_direct.mjs       # Test: MCP socket connection
└── test_mcp_socket.py        # Test: MCP socket (Python)
```

---

## 🔍 Redis Bridge: Command & Response Flow

### Message Format (Request)

```json
{
  "v": "1.0",
  "trace_id": "uuid-1234-5678",
  "span_id": "uuid-abcd-efgh",
  "ts": 1696531234,
  "cmd": "CreateCube",
  "params": {
    "name": "MyCube",
    "location": [0, 0, 0],
    "size": 2.0
  },
  "opts": {
    "timeout_ms": 10000,
    "reply_stream": "blender:reply"
  }
}
```

**Key Fields**:
- `trace_id`: Unique ID to match request/response (for distributed tracing)
- `span_id`: Sub-operation ID (useful for nested operations)
- `ts`: Unix timestamp
- `cmd`: Command name (PascalCase convention)
- `params`: Command-specific parameters
- `opts`: Execution options (timeout, reply stream, etc.)

### Message Format (Response)

```json
{
  "v": "1.0",
  "trace_id": "uuid-1234-5678",
  "span_id": "uuid-abcd-efgh",
  "ts": 1696531235,
  "status": "ok",
  "cmd": "CreateCube",
  "result": {
    "name": "MyCube",
    "location": [0, 0, 0],
    "size": 2.0,
    "vertex_count": 8,
    "face_count": 6
  },
  "metrics": {
    "cpu_ms": 15,
    "wall_ms": 23,
    "queue_wait_ms": 2,
    "exec_ms": 21
  }
}
```

**Key Fields**:
- `status`: "ok" or "error"
- `result`: Command result data
- `metrics`: Performance metrics
  - `cpu_ms`: CPU time
  - `wall_ms`: Total wall-clock time
  - `queue_wait_ms`: Time waiting in queue
  - `exec_ms`: Actual execution time

### Error Response

```json
{
  "v": "1.0",
  "trace_id": "uuid-1234-5678",
  "status": "error",
  "cmd": "CreateCube",
  "error": {
    "code": "INVALID_PARAM",
    "message": "location must be [x, y, z]",
    "details": {
      "param": "location",
      "received": "invalid"
    }
  }
}
```

---

## 🎮 Available Commands

### Basic Commands

#### `Ping`
**Purpose**: Health check, verify connection  
**Parameters**:
```json
{
  "echo": "any string"
}
```
**Response**:
```json
{
  "echo": "any string",
  "sidecar_version": "2.0.0-realtime",
  "worker_id": "worker-001",
  "blender_version": "5.0.0 Alpha",
  "blender_build": "darwin-arm64",
  "ts": 1696531234
}
```

#### `CreateCube`
**Purpose**: Create a cube mesh  
**Parameters**:
```json
{
  "name": "MyCube",
  "location": [0, 0, 0],
  "size": 2.0
}
```
**Response**:
```json
{
  "name": "MyCube",
  "location": [0, 0, 0],
  "size": 2.0,
  "vertex_count": 8,
  "face_count": 6
}
```

#### `CreateRoom`
**Purpose**: Create a room with walls, floor, ceiling  
**Parameters**:
```json
{
  "name": "StartRoom",
  "location": [0, 0, 0],
  "width": 10.0,
  "depth": 10.0,
  "height": 3.0
}
```
**Response**:
```json
{
  "name": "StartRoom",
  "location": [0, 0, 0],
  "width": 10.0,
  "depth": 10.0,
  "height": 3.0,
  "objects_created": [
    "StartRoom_Floor",
    "StartRoom_Ceiling",
    "StartRoom_Wall_North",
    "StartRoom_Wall_South",
    "StartRoom_Wall_East",
    "StartRoom_Wall_West"
  ]
}
```

### Dungeon Commands

#### `CreateDungeon`
**Purpose**: Generate a complete dungeon with rooms, corridors, lights  
**Parameters**:
```json
{
  "size": 12,
  "rooms": 7,
  "style": "medieval",
  "add_lights": true,
  "add_player": true
}
```
**Response**:
```json
{
  "dungeon_name": "Dungeon_medieval_1696531234",
  "rooms_created": 7,
  "corridors_created": 6,
  "lights_created": 28,
  "objects_created": [
    "Room_0",
    "Room_1",
    // ... more objects
  ],
  "time_taken": 0.342,
  "message": "🏰 Dungeon 'Dungeon_medieval_1696531234' created with 7 rooms and 47 objects in 0.34s!"
}
```

#### `GetDungeonStats`
**Purpose**: Get statistics about the current dungeon  
**Parameters**: `{}`  
**Response**:
```json
{
  "stats": {
    "total_objects": 47,
    "rooms": 7,
    "corridors": 6,
    "walls": 28,
    "lights": 28,
    "decorations": 12
  },
  "message": "📊 Dungeon stats: 7 rooms, 28 walls, 28 lights"
}
```

#### `AnimateDungeon`
**Purpose**: Animate torch lights with flickering effect  
**Parameters**:
```json
{
  "intensity": 0.3,
  "speed": 1.0,
  "duration": 120
}
```
**Response**:
```json
{
  "lights_animated": [
    "Torch_1_2_0",
    "Torch_1_2_1",
    // ... more lights
  ],
  "duration": 120,
  "message": "🔥 Animated 28 torches with flickering!"
}
```

---

## 🧪 Testing & Learning

### Test 1: Basic Connection
**File**: `orchestrator/src/examples/test-ping.js`

```javascript
import { BlenderClient } from '../lib/blender-client.js';

const client = new BlenderClient();
const response = await client.ping('Hello from orchestrator!');
console.log('Blender version:', response.result.blender_version);
await client.close();
```

**What We Learn**:
- Redis connection works
- Request/response cycle
- Trace ID matching
- Response timing

### Test 2: Single Cube Creation
**File**: `orchestrator/src/examples/test-cube.js`

```javascript
const response = await client.createCube({
  name: 'TestCube',
  location: [5, 5, 0],
  size: 2.0
});

console.log('Created:', response.result.name);
console.log('Vertices:', response.result.vertex_count);
```

**What We Learn**:
- Command parameters
- Blender object creation
- Mesh properties
- Performance metrics

### Test 3: Room Creation
**File**: `orchestrator/src/examples/test-room.js`

```javascript
const response = await client.createRoom({
  name: 'StartRoom',
  location: [0, 0, 0],
  width: 10,
  depth: 10,
  height: 3
});

console.log('Room objects:', response.result.objects_created);
```

**What We Learn**:
- Composite operations (room = floor + walls + ceiling)
- Object naming conventions
- Hierarchical operations
- Multi-object creation

### Test 4: Full Dungeon
**File**: `test_dungeon.mjs`

```javascript
// 1. Verify version
const pingResult = await sendCommand('Ping', { echo: 'version check' });

// 2. Build dungeon
const dungeonResult = await sendCommand('CreateDungeon', {
  size: 12,
  rooms: 7,
  style: 'medieval',
  add_lights: true,
  add_player: true
});

// 3. Get stats
const statsResult = await sendCommand('GetDungeonStats', {});

// 4. Animate torches
const animResult = await sendCommand('AnimateDungeon', {
  intensity: 0.3,
  speed: 1.0,
  duration: 120
});
```

**What We Learn**:
- Complex multi-step workflows
- Sequential command execution
- Scene state management
- Animation integration
- Real-time viewport updates (via `bpy.app.timers`)

---

## 🔬 Command Implementation Details

### Sidecar: Command Handler Pattern

**File**: `sidecar/router.py`

```python
class CommandRouter:
    def __init__(self):
        self.handlers = {
            'Ping': ping_handler,
            'CreateCube': create_cube_handler,
            'CreateRoom': create_room_handler,
            'CreateDungeon': create_dungeon_handler,
            # ... more commands
        }
    
    def route(self, cmd, params):
        handler = self.handlers.get(cmd)
        if handler:
            return handler(params)
        else:
            raise CommandNotFoundError(f"Unknown command: {cmd}")
```

### Sidecar: Threading + bpy.app.timers

**File**: `sidecar/consumer.py`

```python
import threading
import bpy

class RedisConsumer:
    def start(self):
        # Background thread for Redis polling (non-blocking!)
        self.thread = threading.Thread(target=self._consumer_loop, daemon=True)
        self.thread.start()
    
    def _consumer_loop(self):
        while True:
            # Read from Redis (blocking on Redis side)
            messages = self.redis.xread(streams={'blender:cmd': '>'})
            
            for message in messages:
                # Queue command for main thread
                bpy.app.timers.register(
                    lambda: self._execute_command(message),
                    first_interval=0.0
                )
    
    def _execute_command(self, message):
        # This runs in Blender's MAIN THREAD
        # Safe to use bpy.ops, bpy.data, etc.
        cmd = message['cmd']
        params = message['params']
        result = self.router.route(cmd, params)
        
        # Send response back via Redis
        self._send_response(result)
```

**Why This Works**:
1. **Background thread** polls Redis (no blocking in main thread)
2. **`bpy.app.timers`** executes commands in main thread (safe for Blender API)
3. **Viewport stays responsive** (no freezing!)
4. **Real-time updates** (objects appear as they're created)

---

## 📊 Logging & Observability

### Orchestrator Logs

```javascript
[BlenderClient] Sending command: CreateCube (trace=uuid-1234)
[BlenderClient] Command succeeded: CreateCube (trace=uuid-1234)
[BlenderClient] Response time: 23ms
```

### Sidecar Logs

```python
[RedisConsumer] Received command: CreateCube (trace=uuid-1234)
[RedisConsumer] Executing in main thread via bpy.app.timers
[CreateCube] Creating cube 'MyCube' at [0, 0, 0] with size 2.0
[CreateCube] Cube created: 8 vertices, 6 faces
[RedisConsumer] Sending response (trace=uuid-1234)
[RedisConsumer] Metrics: cpu=15ms, wall=23ms, queue=2ms, exec=21ms
```

### Performance Metrics

Every response includes:
- **CPU time** (`cpu_ms`): Time spent executing Python code
- **Wall-clock time** (`wall_ms`): Total time from receive to send
- **Queue wait** (`queue_wait_ms`): Time waiting for main thread
- **Execution time** (`exec_ms`): Time spent in Blender API calls

These metrics help us:
- Identify slow commands
- Optimize Blender operations
- Understand threading overhead
- Debug performance issues

---

## 🎨 Dungeon Styles

### Medieval Style
**Colors**: Stone gray, torchlight orange  
**Objects**: Stone walls, wooden doors, torches, pillars  
**Lighting**: Warm flickering torches  

### Sci-Fi Style
**Colors**: Metallic gray/blue, neon accents  
**Objects**: Metal panels, sliding doors, tech lights, consoles  
**Lighting**: Cool blue/cyan lights  

### Fantasy Style
**Colors**: Purple/mystical, magical glow  
**Objects**: Crystal walls, magical runes, glowing orbs  
**Lighting**: Ethereal purple/pink lights  

---

## 🚀 Next Steps: Extending the System

### Planned Commands

#### Geometry Commands
- [ ] `CreateSphere` - Create sphere mesh
- [ ] `CreateCylinder` - Create cylinder mesh
- [ ] `CreatePlane` - Create plane mesh
- [ ] `CreateMesh` - Custom mesh from vertices/faces

#### Transform Commands
- [ ] `TransformObject` - Move/rotate/scale object
- [ ] `DeleteObject` - Remove object from scene
- [ ] `DuplicateObject` - Clone object
- [ ] `JoinObjects` - Merge multiple objects

#### Material Commands
- [ ] `CreateMaterial` - New material
- [ ] `AssignMaterial` - Apply material to object
- [ ] `SetShaderNode` - Node-based shading
- [ ] `SetColor` - Simple object color

#### Scene Commands
- [ ] `GetSceneInfo` - Full scene data
- [ ] `GetObjectList` - List all objects
- [ ] `GetObjectInfo` - Detailed object data
- [ ] `ClearScene` - Delete all objects

#### Animation Commands
- [ ] `SetKeyframe` - Add keyframe
- [ ] `CreateAnimation` - Keyframe sequence
- [ ] `SetAnimationRange` - Timeline settings

#### Import/Export Commands
- [ ] `ImportFBX` - Import FBX file
- [ ] `ExportGLB` - Export to GLB format
- [ ] `SaveBlendFile` - Save .blend file
- [ ] `LoadBlendFile` - Load .blend file

### Advanced Orchestrator Features

#### Dungeon Generator Algorithm
```javascript
class DungeonGenerator {
  async generate(options) {
    // 1. Place rooms using BSP or grid algorithm
    const rooms = this._placeRooms(options);
    
    // 2. Create corridors between rooms
    const corridors = this._createCorridors(rooms);
    
    // 3. Add decorations (pillars, crates, etc.)
    const decorations = this._addDecorations(rooms);
    
    // 4. Place lights
    const lights = this._placeLights(rooms, corridors);
    
    // 5. Set spawn points
    const spawns = this._setSpawnPoints(rooms);
    
    return {
      rooms,
      corridors,
      decorations,
      lights,
      spawns
    };
  }
}
```

#### Room Placer (BSP Algorithm)
```javascript
class RoomPlacer {
  placeRooms(count, minSize, maxSize, dungeonSize) {
    // Binary Space Partitioning
    const tree = this._createBSPTree(dungeonSize, count);
    const rooms = this._extractRooms(tree, minSize, maxSize);
    return rooms;
  }
}
```

#### Corridor Router (A* Pathfinding)
```javascript
class CorridorRouter {
  createCorridor(room1, room2, width) {
    // A* pathfinding between room centers
    const path = this._findPath(room1.center, room2.center);
    
    // Convert path to corridor segments
    const segments = this._pathToSegments(path, width);
    
    return segments;
  }
}
```

---

## 🎓 Lessons Learned

### Threading & Blender API
**Problem**: Blender API is NOT thread-safe. Calling `bpy.ops` from background thread = CRASH.

**Solution**: Use `bpy.app.timers.register()` to queue commands for main thread execution.

```python
# ❌ WRONG: Crashes Blender
def background_thread():
    bpy.ops.mesh.primitive_cube_add()  # CRASH!

# ✅ CORRECT: Safe execution
def background_thread():
    bpy.app.timers.register(
        lambda: bpy.ops.mesh.primitive_cube_add(),
        first_interval=0.0
    )
```

### Redis Streams vs Pub/Sub
**Why Streams?**
- ✅ **Persistence**: Messages survive crashes
- ✅ **Acknowledgment**: Know when message is processed
- ✅ **Consumer groups**: Multiple workers
- ✅ **Ordering**: Messages are ordered
- ✅ **History**: Can replay messages

**Pub/Sub** is fire-and-forget, no persistence, no ack.

### Trace IDs for Debugging
**Problem**: Hard to match requests/responses in logs.

**Solution**: Add `trace_id` and `span_id` to every message.

```javascript
// Request
const trace_id = uuidv4();
redis.xadd('blender:cmd', { trace_id, cmd: 'CreateCube', ... });

// Response (include same trace_id)
redis.xadd('blender:reply', { trace_id, status: 'ok', ... });

// Logs
console.log(`[${trace_id}] Command: CreateCube`);
console.log(`[${trace_id}] Response: ok (23ms)`);
```

Now we can **trace entire workflows** across orchestrator and sidecar!

### Performance: Batch Commands
**Problem**: Creating 100 objects = 100 round trips to Redis = slow.

**Solution**: Add batch command support.

```javascript
// Instead of:
for (let i = 0; i < 100; i++) {
  await client.createCube({ location: [i, 0, 0] });
}

// Do:
await client.batchCommands([
  { cmd: 'CreateCube', params: { location: [0, 0, 0] } },
  { cmd: 'CreateCube', params: { location: [1, 0, 0] } },
  // ... 100 commands
]);
```

**Result**: 1 round trip instead of 100!

---

## 🎯 Success Metrics

### Current Status (October 5, 2025)

- ✅ Redis bridge working (threading fixed!)
- ✅ Basic commands: Ping, CreateCube, CreateRoom
- ✅ Dungeon generation: CreateDungeon, AnimateDungeon
- ✅ Real-time viewport updates (bpy.app.timers)
- ✅ Orchestrator project created
- ✅ Test scripts working
- ⏳ Documentation in progress (this file!)

### Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Ping | ~20ms | Round trip to Blender |
| CreateCube | ~25ms | Single cube mesh |
| CreateRoom | ~150ms | Floor + 4 walls + ceiling |
| CreateDungeon (7 rooms) | ~350ms | 47 objects total |
| AnimateDungeon (28 lights) | ~160ms | Keyframe animation |

**Target**: <100ms for simple commands, <1s for complex dungeons

---

## 🔮 Future Vision

### Phase 1: Solid Foundation (Current)
- ✅ Redis bridge + threading
- ✅ Basic primitives (cube, room)
- ✅ Simple dungeon generation
- ⏳ Documentation

### Phase 2: Rich Command Library (Next 2 Weeks)
- [ ] 50+ Blender operations exposed
- [ ] Geometry nodes support
- [ ] Material/shading system
- [ ] Import/export commands

### Phase 3: Advanced Orchestration (Month 1)
- [ ] Sophisticated dungeon algorithms (BSP, cellular automata)
- [ ] Biome system (medieval, sci-fi, fantasy, horror)
- [ ] Procedural decorations
- [ ] Lighting presets
- [ ] Camera automation

### Phase 4: Game Engine Integration (Month 2)
- [ ] Export to game engines (Unity, Unreal, Godot)
- [ ] Navmesh generation
- [ ] Collision mesh optimization
- [ ] LOD generation
- [ ] Asset packing

### Phase 5: AI Integration (Month 3+)
- [ ] AI-driven dungeon design ("make it spookier")
- [ ] Style transfer
- [ ] Intelligent decoration placement
- [ ] Automated testing (playability)

---

## 📝 Change Log

### October 5, 2025 - Project Start
- Created orchestrator project
- Moved orchestrator into blender repo
- Updated .gitignore
- Created this learning document
- Current commands: Ping, CreateCube, CreateRoom, CreateDungeon, AnimateDungeon

### Next Entry (TBD)
- (Document new commands and learnings here)

---

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new commands
- Improve algorithms
- Optimize performance
- Enhance documentation
- Report bugs
- Share learnings

**Keep the division of responsibilities clear**:
- Orchestrator = Game logic & algorithms
- Sidecar = Blender primitives only

---

**Degenerate Labs** - Building dungeons, learning Blender automation! 🚀🏰

