# Redis Bridge: Data Objects & Message Schema

**Purpose**: Complete reference for all data structures, commands, and responses flowing over the Redis bridge.

**Last Updated**: October 5, 2025

---

## 📋 Message Envelope (Request)

Every command sent to Blender follows this structure:

```typescript
interface CommandRequest {
  v: string;           // Protocol version (e.g., "1.0")
  trace_id: string;    // UUID for request tracing
  span_id: string;     // UUID for sub-operation tracing
  ts: number;          // Unix timestamp (seconds)
  cmd: string;         // Command name (PascalCase)
  params: object;      // Command-specific parameters
  opts: {
    timeout_ms: number;      // Command timeout in milliseconds
    reply_stream: string;    // Redis stream for response
    [key: string]: any;      // Additional options
  };
}
```

### Example Request

```json
{
  "v": "1.0",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "ts": 1696531234,
  "cmd": "CreateCube",
  "params": {
    "name": "TestCube",
    "location": [0, 0, 0],
    "size": 2.0
  },
  "opts": {
    "timeout_ms": 10000,
    "reply_stream": "blender:reply:orchestrator"
  }
}
```

---

## 📋 Message Envelope (Response)

Every response from Blender follows this structure:

```typescript
interface CommandResponse {
  v: string;           // Protocol version
  trace_id: string;    // Same as request
  span_id: string;     // Same as request
  ts: number;          // Response timestamp
  status: "ok" | "error";
  cmd: string;         // Command name (echo from request)
  result?: object;     // Success result (if status="ok")
  error?: {            // Error details (if status="error")
    code: string;
    message: string;
    details?: object;
  };
  metrics: {
    cpu_ms: number;        // CPU time
    wall_ms: number;       // Wall-clock time
    queue_wait_ms: number; // Time in queue
    exec_ms: number;       // Execution time
  };
}
```

### Example Success Response

```json
{
  "v": "1.0",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "ts": 1696531235,
  "status": "ok",
  "cmd": "CreateCube",
  "result": {
    "name": "TestCube",
    "location": [0, 0, 0],
    "size": 2.0,
    "vertex_count": 8,
    "face_count": 6,
    "blender_object_name": "TestCube"
  },
  "metrics": {
    "cpu_ms": 15,
    "wall_ms": 23,
    "queue_wait_ms": 2,
    "exec_ms": 21
  }
}
```

### Example Error Response

```json
{
  "v": "1.0",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "ts": 1696531235,
  "status": "error",
  "cmd": "CreateCube",
  "error": {
    "code": "INVALID_PARAM",
    "message": "Parameter 'location' must be array of 3 numbers",
    "details": {
      "param": "location",
      "received": "invalid",
      "expected": "[x, y, z]"
    }
  },
  "metrics": {
    "cpu_ms": 2,
    "wall_ms": 5,
    "queue_wait_ms": 1,
    "exec_ms": 4
  }
}
```

---

## 🎮 Command Reference

### Ping

**Command**: `Ping`  
**Purpose**: Health check, verify connection and get system info  

**Parameters**:
```typescript
{
  echo?: string;  // Optional message to echo back
}
```

**Response**:
```typescript
{
  echo: string;              // Echoed message (or default)
  sidecar_version: string;   // Sidecar version (e.g., "2.0.0-realtime")
  worker_id: string;         // Worker identifier
  hostname: string;          // System hostname
  blender_version: string;   // Blender version (e.g., "5.0.0 Alpha")
  blender_build: string;     // Build platform (e.g., "darwin-arm64")
  ts: number;                // Timestamp
}
```

**Example**:
```json
// Request
{
  "cmd": "Ping",
  "params": { "echo": "Hello Blender!" }
}

// Response
{
  "status": "ok",
  "result": {
    "echo": "Hello Blender!",
    "sidecar_version": "2.0.0-realtime",
    "worker_id": "worker-001",
    "hostname": "macbook-pro.local",
    "blender_version": "5.0.0 Alpha",
    "blender_build": "darwin-arm64",
    "ts": 1696531234
  }
}
```

---

### CreateCube

**Command**: `CreateCube`  
**Purpose**: Create a cube mesh primitive  

**Parameters**:
```typescript
{
  name?: string;       // Object name (default: "Cube")
  location?: [number, number, number];  // XYZ position (default: [0, 0, 0])
  size?: number;       // Cube size (default: 2.0)
}
```

**Response**:
```typescript
{
  name: string;              // Object name
  location: [number, number, number];  // Position
  size: number;              // Size
  vertex_count: number;      // Number of vertices (8 for cube)
  face_count: number;        // Number of faces (6 for cube)
  blender_object_name: string;  // Internal Blender name
}
```

**Example**:
```json
// Request
{
  "cmd": "CreateCube",
  "params": {
    "name": "MyCube",
    "location": [5, 10, 0],
    "size": 3.0
  }
}

// Response
{
  "status": "ok",
  "result": {
    "name": "MyCube",
    "location": [5, 10, 0],
    "size": 3.0,
    "vertex_count": 8,
    "face_count": 6,
    "blender_object_name": "MyCube"
  }
}
```

---

### CreateRoom

**Command**: `CreateRoom`  
**Purpose**: Create a room with floor, ceiling, and walls  

**Parameters**:
```typescript
{
  name?: string;       // Room name (default: "Room")
  location?: [number, number, number];  // Center position
  width?: number;      // Room width (X axis, default: 10.0)
  depth?: number;      // Room depth (Y axis, default: 10.0)
  height?: number;     // Room height (Z axis, default: 3.0)
}
```

**Response**:
```typescript
{
  name: string;
  location: [number, number, number];
  width: number;
  depth: number;
  height: number;
  objects_created: string[];  // Array of created object names
}
```

**Example**:
```json
// Request
{
  "cmd": "CreateRoom",
  "params": {
    "name": "StartRoom",
    "location": [0, 0, 0],
    "width": 10,
    "depth": 10,
    "height": 3
  }
}

// Response
{
  "status": "ok",
  "result": {
    "name": "StartRoom",
    "location": [0, 0, 0],
    "width": 10,
    "depth": 10,
    "height": 3,
    "objects_created": [
      "StartRoom_Floor",
      "StartRoom_Ceiling",
      "StartRoom_Wall_North",
      "StartRoom_Wall_South",
      "StartRoom_Wall_East",
      "StartRoom_Wall_West"
    ]
  }
}
```

---

### CreateDungeon

**Command**: `CreateDungeon`  
**Purpose**: Generate a complete dungeon with rooms, corridors, lights, and decorations  

**Parameters**:
```typescript
{
  size?: number;           // Grid size (default: 12)
  rooms?: number;          // Number of rooms (default: 7)
  style?: "medieval" | "sci-fi" | "fantasy";  // Visual style
  add_lights?: boolean;    // Add torch/light sources (default: true)
  add_player?: boolean;    // Add player spawn point (default: true)
  add_decorations?: boolean;  // Add pillars, crates, etc. (default: false)
}
```

**Response**:
```typescript
{
  dungeon_name: string;          // Generated dungeon name
  rooms_created: number;         // Number of rooms
  corridors_created: number;     // Number of corridors
  lights_created: number;        // Number of lights
  objects_created: string[];     // Array of all object names
  time_taken: number;            // Build time in seconds
  message: string;               // Human-readable summary
}
```

**Example**:
```json
// Request
{
  "cmd": "CreateDungeon",
  "params": {
    "size": 15,
    "rooms": 10,
    "style": "medieval",
    "add_lights": true,
    "add_player": true
  }
}

// Response
{
  "status": "ok",
  "result": {
    "dungeon_name": "Dungeon_medieval_1696531234",
    "rooms_created": 10,
    "corridors_created": 9,
    "lights_created": 40,
    "objects_created": [
      "Room_0",
      "Room_1",
      "Corridor_0_1",
      "Torch_0_0",
      // ... more objects
    ],
    "time_taken": 0.456,
    "message": "🏰 Dungeon 'Dungeon_medieval_1696531234' created with 10 rooms and 89 objects in 0.46s!"
  }
}
```

---

### GetDungeonStats

**Command**: `GetDungeonStats`  
**Purpose**: Get statistics about the current scene/dungeon  

**Parameters**: `{}` (none)

**Response**:
```typescript
{
  stats: {
    total_objects: number;
    rooms: number;
    corridors?: number;
    walls?: number;
    lights?: number;
    decorations?: number;
    [key: string]: number;  // Additional stats
  };
  message: string;
}
```

**Example**:
```json
// Request
{
  "cmd": "GetDungeonStats",
  "params": {}
}

// Response
{
  "status": "ok",
  "result": {
    "stats": {
      "total_objects": 89,
      "rooms": 10,
      "corridors": 9,
      "walls": 60,
      "lights": 40,
      "decorations": 15
    },
    "message": "📊 Dungeon stats: 10 rooms, 60 walls, 40 lights"
  }
}
```

---

### AnimateDungeon

**Command**: `AnimateDungeon`  
**Purpose**: Animate torch lights with flickering effect  

**Parameters**:
```typescript
{
  intensity?: number;   // Flicker intensity 0.0-1.0 (default: 0.3)
  speed?: number;       // Animation speed (default: 1.0)
  duration?: number;    // Duration in frames (default: 120)
}
```

**Response**:
```typescript
{
  lights_animated: string[];  // Array of light names
  duration: number;           // Animation duration (frames)
  message: string;
}
```

**Example**:
```json
// Request
{
  "cmd": "AnimateDungeon",
  "params": {
    "intensity": 0.5,
    "speed": 1.5,
    "duration": 240
  }
}

// Response
{
  "status": "ok",
  "result": {
    "lights_animated": [
      "Torch_0_0",
      "Torch_0_1",
      "Torch_1_0",
      // ... more lights
    ],
    "duration": 240,
    "message": "🔥 Animated 40 torches with flickering!"
  }
}
```

---

## 🚨 Error Codes

### Common Error Codes

| Code | Description | Example |
|------|-------------|---------|
| `UNKNOWN_COMMAND` | Command not recognized | Sent "CreateSphere" but not implemented |
| `INVALID_PARAM` | Invalid parameter value | location is "abc" instead of [x,y,z] |
| `MISSING_PARAM` | Required parameter missing | CreateCube without location |
| `BLENDER_ERROR` | Blender API error | bpy.ops failed |
| `TIMEOUT` | Command exceeded timeout | Took > timeout_ms |
| `INTERNAL_ERROR` | Unexpected error | Python exception |

### Error Response Structure

```typescript
{
  code: string;        // Error code (see table above)
  message: string;     // Human-readable error message
  details?: {          // Optional additional details
    [key: string]: any;
  };
}
```

---

## 📊 Performance Metrics

Every response includes performance metrics:

```typescript
{
  cpu_ms: number;        // CPU time spent executing
  wall_ms: number;       // Total elapsed time
  queue_wait_ms: number; // Time waiting in queue
  exec_ms: number;       // Actual execution time
}
```

**Interpretation**:
- **cpu_ms**: Pure Python execution time
- **wall_ms**: Total time from receive to send (including queuing)
- **queue_wait_ms**: Time waiting for main thread (`bpy.app.timers`)
- **exec_ms**: Time spent in Blender API calls

**Example**:
```json
{
  "cpu_ms": 15,      // 15ms of Python code
  "wall_ms": 23,     // 23ms total (includes 2ms queue wait)
  "queue_wait_ms": 2, // 2ms waiting for main thread
  "exec_ms": 21      // 21ms in Blender operations
}
```

---

## 🔍 Tracing & Debugging

### Trace IDs

Every request/response pair shares a `trace_id`:

```javascript
// Orchestrator sends:
const trace_id = uuidv4();
redis.xadd('blender:cmd', {
  payload: JSON.stringify({
    trace_id,
    cmd: 'CreateCube',
    // ...
  })
});

// Blender responds with SAME trace_id:
redis.xadd('blender:reply', {
  payload: JSON.stringify({
    trace_id,  // SAME!
    status: 'ok',
    // ...
  })
});
```

### Span IDs

For nested operations, use `span_id`:

```javascript
// Parent operation
const trace_id = uuidv4();
const parent_span = uuidv4();

// Child operation 1
const child_span_1 = uuidv4();
await sendCommand({
  trace_id,     // Same trace_id
  span_id: child_span_1,
  parent_span,  // Link to parent
  cmd: 'CreateRoom',
});

// Child operation 2
const child_span_2 = uuidv4();
await sendCommand({
  trace_id,     // Same trace_id
  span_id: child_span_2,
  parent_span,  // Link to parent
  cmd: 'CreateCube',
});
```

### Log Format

**Orchestrator logs**:
```
[2025-10-05 14:23:45] [trace=550e8400] Sending: CreateCube
[2025-10-05 14:23:45] [trace=550e8400] Response: ok (23ms)
```

**Sidecar logs**:
```
[2025-10-05 14:23:45] [trace=550e8400] Received: CreateCube
[2025-10-05 14:23:45] [trace=550e8400] Queued for main thread
[2025-10-05 14:23:45] [trace=550e8400] Executing in main thread
[2025-10-05 14:23:45] [trace=550e8400] Success (exec=21ms)
[2025-10-05 14:23:45] [trace=550e8400] Sent response
```

---

## 🔧 Redis Streams

### Stream Names

| Stream | Purpose | Direction |
|--------|---------|-----------|
| `blender:cmd` | Commands to Blender | Orchestrator → Blender |
| `blender:reply` | Responses from Blender | Blender → Orchestrator |
| `blender:reply:<id>` | Worker-specific replies | Blender → Specific worker |

### Message Structure in Redis

Redis Streams store messages as field-value pairs:

```
> XREAD STREAMS blender:cmd 0
1) 1) "blender:cmd"
   2) 1) 1) "1696531234567-0"
         2) 1) "payload"
            2) "{\"v\":\"1.0\",\"trace_id\":\"...\",\"cmd\":\"CreateCube\",...}"
```

**Fields**:
- `payload`: JSON string of CommandRequest or CommandResponse

---

## 📝 TypeScript Type Definitions

For TypeScript projects using the orchestrator:

```typescript
// types/blender-bridge.d.ts

export interface CommandRequest {
  v: string;
  trace_id: string;
  span_id: string;
  ts: number;
  cmd: string;
  params: Record<string, any>;
  opts: {
    timeout_ms: number;
    reply_stream: string;
    [key: string]: any;
  };
}

export interface CommandResponse {
  v: string;
  trace_id: string;
  span_id: string;
  ts: number;
  status: "ok" | "error";
  cmd: string;
  result?: Record<string, any>;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  metrics: {
    cpu_ms: number;
    wall_ms: number;
    queue_wait_ms: number;
    exec_ms: number;
  };
}

// Command-specific types
export interface PingParams {
  echo?: string;
}

export interface PingResult {
  echo: string;
  sidecar_version: string;
  worker_id: string;
  hostname: string;
  blender_version: string;
  blender_build: string;
  ts: number;
}

export interface CreateCubeParams {
  name?: string;
  location?: [number, number, number];
  size?: number;
}

export interface CreateCubeResult {
  name: string;
  location: [number, number, number];
  size: number;
  vertex_count: number;
  face_count: number;
  blender_object_name: string;
}

// ... more command types
```

---

## 🎯 Best Practices

### 1. Always Include trace_id

```javascript
// ✅ GOOD
const trace_id = uuidv4();
await sendCommand({ trace_id, cmd: 'CreateCube', ... });

// ❌ BAD
await sendCommand({ cmd: 'CreateCube', ... });  // No way to trace!
```

### 2. Handle Errors Gracefully

```javascript
try {
  const response = await client.createCube({ ... });
  console.log('Success:', response.result);
} catch (error) {
  if (error.code === 'INVALID_PARAM') {
    console.error('Fix parameters:', error.details);
  } else if (error.code === 'TIMEOUT') {
    console.error('Increase timeout or simplify operation');
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### 3. Use Appropriate Timeouts

```javascript
// Simple operation: 5 seconds
await client.createCube({ ... }, { timeout: 5000 });

// Complex operation: 30 seconds
await client.createDungeon({ ... }, { timeout: 30000 });
```

### 4. Log Performance Metrics

```javascript
const response = await client.createCube({ ... });

console.log('Command completed:');
console.log(`  Total time: ${response.metrics.wall_ms}ms`);
console.log(`  Queue wait: ${response.metrics.queue_wait_ms}ms`);
console.log(`  Execution: ${response.metrics.exec_ms}ms`);
```

---

## 🔮 Future Message Types

### Planned Commands

- **Geometry**: CreateSphere, CreateCylinder, CreateMesh
- **Transform**: TransformObject, DeleteObject, JoinObjects
- **Materials**: CreateMaterial, AssignMaterial, SetColor
- **Scene**: GetSceneInfo, GetObjectList, ClearScene
- **Export**: ExportGLB, ExportFBX, SaveBlendFile

See `REDIS_BRIDGE_PLAN.md` for complete roadmap.

---

**Last Updated**: October 5, 2025  
**Degenerate Labs** - Building the future of Blender automation! 🚀

