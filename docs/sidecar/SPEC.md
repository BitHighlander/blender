# Blender Python Sidecar ↔ Redis Bridge — Planning Doc (SPEC)

**Version:** 1.0  
**Last Updated:** October 5, 2025

---

## Overview

**Scope:** This spec defines a minimal but comprehensive "Python sidecar" that runs inside headless Blender and exposes a stable, efficient command API over Redis.

**Non-scope:** Dungeon math, worldgen logic, game scripts, and any heavy business logic live in your middle project (the orchestrator). The sidecar is just a thin bridge to the Blender Python API and file exports.

---

## 0) Design Principles

1. **Minimal Surface**: Only primitives to manipulate Blender data, evaluate, and export. No domain logic.

2. **Deterministic & Idempotent**: Every command accepts an `idempotency_key`. Safe to retry.

3. **Efficient I/O**: Compact JSON/MessagePack payloads; optional Zstandard compression; large blobs by reference (paths/URIs).

4. **Observable**: Rich, structured errors; per-command metrics; trace/span IDs; progress events.

5. **Isolated & Reproducible**: One job per fresh process where practical; no lingering UI state; undo disabled during bulk ops.

6. **Versioned**: Schema and feature flags gate behavior; old orchestrators can talk to new sidecars safely.

---

## 1) Runtime & Process Model

- **Launch**: `blender -b <factory.blend> --python sidecar.py`

- Single-threaded bpy access (Blender main thread). Parallelism via multiple processes/containers (N workers).

- No UI operators except guarded fallbacks; prefer RNA/Data API/Geometry Nodes.

- Global Undo disabled during mutations; re-enabled after.

- Ephemeral workspace: Each job creates an in-memory Scene and optional temp `.blend`; cleans up on completion.

---

## 2) Redis Topology

### Command ingress
- **Redis Streams** for reliability & backpressure
- Stream: `blender:cmd`
- Consumer group per deployment: `cg:<deployment>`

### Result egress
- Per-command reply stream (`reply_stream` in request), default `blender:reply`

### Logs & progress
- Stream `blender:events` (structured events)
- Optional Pub/Sub for live tails

### Health & metrics
- Hash `blender:health:<worker_id>`, updated via heartbeat
- Stream `blender:metrics`

**Why Streams?** Ack/replay semantics, multi-consumer safety, ordering per command, and durability.

---

## 3) Envelope & Message Schema

### 3.1 Request (Stream entry value)

```json
{
  "v": "1.0",
  "trace_id": "uuid",
  "span_id": "uuid",
  "idempotency_key": "uuid-or-hash",
  "ts": 1733376000,
  "cmd": "CreateScene",
  "params": { "...": "..." },
  "opts": {
    "timeout_ms": 600000,
    "priority": 5,
    "reply_stream": "blender:reply",
    "compress": "zstd|none",
    "dry_run": false,
    "context": { "scene": "optional-scene-name" }
  }
}
```

### 3.2 Response

```json
{
  "v": "1.0",
  "trace_id": "uuid",
  "span_id": "uuid",
  "status": "ok|error|partial",
  "cmd": "CreateScene",
  "result": { "...": "..." },
  "error": { 
    "code": "E_xxx", 
    "message": "string", 
    "details": { } 
  },
  "metrics": {
    "cpu_ms": 123,
    "wall_ms": 456,
    "mem_mb": 512,
    "depsgraph_updates": 2
  },
  "artifacts": [
    { 
      "type": "file", 
      "mime": "model/gltf-binary", 
      "uri": "file:///.../tile_12.glb", 
      "bytes": 1048576 
    }
  ],
  "logs": [
    { "lvl": "info", "msg": "Created scene tile_12", "ts": 1733376001 }
  ]
}
```

**Compression**: If `compress=zstd`, the request params (and optionally result) are zstd-compressed MessagePack; envelope stays JSON UTF-8 for debuggability.

---

## 4) Command Set (Minimal Primitives)

**Goal:** Cover data creation, asset linking/instancing, GN parameterization, evaluation, export, and housekeeping. Anything more complex belongs in the orchestrator.

### 4.1 Session & Health

#### Ping
- **cmd**: `Ping`
- **params**: `{ "echo": "..." }`
- **result**: `{ "echo": "...", "blender_version": "4.2.x", "sidecar": "1.0.x", "worker_id": "..." }`

#### GetCapabilities
- Reports feature flags: GN version, exporters available, OSL/Cycles support, headless bake availability.

#### Heartbeat (sidecar → Redis)
- Key: `blender:health:<worker_id>` (hash with ts, load, job_id, scene, mem_mb)

### 4.2 Scene & Data Lifecycle

#### CreateScene
- **params**: `{ "name": "scene_id", "units_per_meter": 1.0, "clear_existing": true }`
- Allocates a clean scene; sets units; returns scene handle.

#### LoadBlend
- **params**: `{ "filepath": "/path/file.blend", "link": true|false, "collections": ["COL_A", "COL_B"] }`
- Links/loads assets; returns list of loaded datablocks.

#### SaveBlend
- **params**: `{ "filepath": "/tmp/out.blend", "compress": true }`

#### PurgeOrphans
- Removes unused datablocks; returns counts freed.

### 4.3 Collections, Objects, Instances

#### CreateCollection
- **params**: `{ "name": "ROOMS", "parent": "Scene" }`

#### InstanceCollection
- **params**: `{ "collection": "COL_RoomRect", "name": "room_r12", "parent_collection": "ROOMS", "transform": { "pos":[x,y,z], "rot_euler":[rx,ry,rz], "scale":[sx,sy,sz] } }`
- **result**: Returns object name & world matrix.

#### InstanceCollectionMany
- Vectorized version accepting arrays to avoid per-element loops.

#### CreateMeshFromSpec
- Minimal parametric shells (rect rooms, corridor ribbons) from numeric specs; avoids operators.

#### SetCustomProps
- **params**: `{ "target": "obj|collection|scene", "name": "room_r12", "props": { "room_type":"barracks", "depth":3 } }`

### 4.4 Geometry Nodes (GN) Controls

#### AttachNodeGroup
- **params**: `{ "object":"room_r12", "node_group":"NG_RoomShell", "modifier_name":"GN_RoomShell" }`

#### SetNodeParams
- **params**: `{ "object":"room_r12", "modifier":"GN_RoomShell", "params": { "width": 12.0, "height": 8.0, "ceil": 3.5 } }`

#### SetNamedAttributes
- Push named attributes (e.g., biome_forest, slope) to drive GN.

### 4.5 Evaluation

#### EvaluateDepsgraph
- Forces evaluation; returns timings and changed datablocks count.

#### RealizeInstances
- Converts instances to real meshes via evaluated depsgraph (operator-free path); returns counts.

### 4.6 Export & Manifests

#### ExportGLTF
- **params**: `{ "filepath": "/out/world.glb", "selection": ["ROOMS","PROPS"], "apply_modifiers": true, "materials":"pbr", "extras": { "embed_buffers": true } }`
- **result**: `{ "filepath": "...", "bytes": 12345678, "node_manifest": "file:///.../manifest.json" }`

#### WriteManifest
- Emits a compact manifest JSON containing:
  - Node names → transforms
  - Collections → purpose tags (`_COLLIDERS`, `_MARKERS`)
  - Custom properties (for `.hyp` component mapping)

### 4.7 Import/Embed External Assets

#### ImportGLB
- Reference third-party glb into the scene (for props/doors) and place instance(s).

#### AssignMaterialPreset
- Apply standardized PBR materials by name.

### 4.8 Diagnostics & Recovery

#### GetSceneSummary
- Counts by type; memory estimate; bounding boxes; instance/realized stats.

#### GetLastError
- Returns the last structured error with traceback (if enabled).

#### CleanupTemp
- Removes temp files created by this job.

---

## 5) Error Model

Error envelope:

```json
{
  "code": "E_SCENE_NOT_FOUND",
  "message": "human-readable",
  "details": { "args": {...}, "blender_ids": [...] },
  "retryable": true
}
```

**Error Codes:**
- `E_SCENE_NOT_FOUND`
- `E_COLLECTION_MISSING`
- `E_EXPORT_FAIL`
- `E_TIMEOUT`
- `E_INVALID_PARAMS`
- `E_UNSUPPORTED_VERSION`
- etc.

**Idempotency:**
- Replays return previous result (if available) with `status:"ok"`, `replayed:true`.

---

## 6) Performance & Efficiency

### Batching
Orchestrator should aggregate small edits into one command (`Batch`), which sidecar executes atomically:

```json
{ 
  "cmd":"Batch", 
  "params":{ 
    "ops":[
      {"cmd":"InstanceCollection",...},
      {"cmd":"SetNodeParams",...}
    ] 
  } 
}
```

### Large payloads
Use URI references (`file://`, `s3://`) for geometry/heightmaps; the sidecar reads locally-mounted paths.

### Compression
`params` may be MsgPack+zstd; sidecar auto-detects by `opts.compress`.

### No per-element loops
Commands are vectorized (e.g., `InstanceCollectionMany` with arrays).

---

## 7) Observability & Telemetry

### Structured events (to `blender:events`)
- Types: `start`, `progress`, `log`, `warning`, `error`, `finish`
- Include `trace_id`, `span_id`, `cmd`, `job_id`, `percent`, `message`

### Metrics (to `blender:metrics`)
- Per-command timing, depsgraph cost, export bytes, realized instance counts

### Trace correlation
- Propagate `trace_id` from orchestrator; sub-spans within sidecar

---

## 8) Security & Safety

1. **Path allowlist**: Only operate under approved directories (e.g., `/assets`, `/build`, `/tmp/sidecar`).

2. **No arbitrary exec**: Commands whitelist only; no eval/exec.

3. **Resource caps**: Max export size, max object count, timeouts per command (abort job safely).

4. **Sandbox materials**: Only approved nodegroups/material presets.

---

## 9) Configuration

### sidecar.toml

```toml
[redis]
url = "redis://:pass@host:6379/0"
cmd_stream = "blender:cmd"
reply_stream_default = "blender:reply"
group = "cg:prod"
consumer = "worker-01"

[paths]
assets_root = "/mnt/assets"
build_root  = "/mnt/build"
tmp_root    = "/tmp/sidecar"

[features]
use_zstd = true
use_msgpack = true
allow_ops_fallback = false  # avoid UI operators in headless

[limits]
max_objects = 200000
max_glb_mb = 500
cmd_timeout_ms = 600000
```

---

## 10) Versioning & Compatibility

- `v` field in every message
- Feature flags advertised via `GetCapabilities`
- Deprecations announced in events stream
- Errors return `E_UNSUPPORTED_VERSION`

---

## 11) Testing Strategy

1. **Unit tests (offline)**: Command handlers via mocked bpy layer

2. **Golden tests**: Same input → identical `manifest.json` & `export.glb` hash

3. **Soak tests**: Batch thousands of `InstanceCollectionMany` to detect leaks

4. **Fault injection**: Simulate Redis disconnect, file permission errors, bad assets

---

## 12) Operational Playbook

- **Scaling**: Increase worker count (more Blender processes) to scale throughput

- **Draining**: Stop reading new commands; finish in-flight; send `drained` event

- **Crash recovery**: On restart, rejoin consumer group; unacked messages re-delivered

- **Profiling knob**: `opts.profile=true` returns per-phase timings (load/link/eval/export)

---

## 13) Example Flows

### A) Build a dungeon scene & export

1. `CreateScene{name: "dgn_042"}`
2. `LoadBlend{filepath:"/mnt/assets/packs/rooms.blend", link:true, collections:["COL_RoomRect","COL_Door_Wood"]}`
3. `InstanceCollectionMany{ parent_collection:"ROOMS", items:[{collection:"COL_RoomRect", name:"r0", transform:{...}}, ...]}`
4. `SetNodeParams` for each shell
5. `EvaluateDepsgraph`
6. `ExportGLTF{ filepath:"/mnt/build/dgn_042.glb", selection:["ROOMS","PROPS","_COLLIDERS"] }`
7. `WriteManifest{ filepath:"/mnt/build/dgn_042.manifest.json" }`
8. `SaveBlend{ filepath:"/mnt/build/dgn_042.blend" }`

### B) Minimal diagnostic

1. `GetSceneSummary` → counts & AABB
2. `GetLastError` if prior command failed

---

## 14) Command Reference (Index)

### Session
- `Ping`
- `GetCapabilities`
- `Heartbeat`

### Scenes/Data
- `CreateScene`
- `SaveBlend`
- `LoadBlend`
- `PurgeOrphans`
- `GetSceneSummary`

### Collections/Objects
- `CreateCollection`
- `InstanceCollection`
- `InstanceCollectionMany`
- `CreateMeshFromSpec`
- `SetCustomProps`

### Geometry Nodes
- `AttachNodeGroup`
- `SetNodeParams`
- `SetNamedAttributes`

### Evaluation
- `EvaluateDepsgraph`
- `RealizeInstances`

### IO
- `ExportGLTF`
- `ImportGLB`
- `AssignMaterialPreset`
- `WriteManifest`

### Utilities
- `Batch`
- `CleanupTemp`
- `GetLastError`

---

## 15) Definition of Done (Sidecar)

1. ✅ Implements all commands above with stable schemas
2. ✅ Deterministic exports; golden manifest/GLB hashes under CI
3. ✅ Backpressure safe (Streams), idempotent, and observable
4. ✅ Docs include examples for each command and expected result
5. ✅ Load & memory stable under target dungeon sizes

---

## Next Steps

1. Scaffold `sidecar.py` with Redis Streams consumer & command router
2. Implement `CreateScene`, `InstanceCollection`, `ExportGLTF`, `WriteManifest` first (vertical slice)
3. Add `Batch`, `EvaluateDepsgraph`, `SetNodeParams` for GN flows
4. Wire CI golden tests on example `dungeon.json` → `manifest.json` + `world.glb`

