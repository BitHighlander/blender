# Blender Python Sidecar ↔ Redis Bridge

> A minimal, production-ready Python sidecar that runs inside headless Blender and exposes a stable command API over Redis Streams.

---

## Overview

This sidecar acts as a **thin bridge** between your orchestrator (game server, worldgen pipeline, etc.) and Blender's Python API (`bpy`). It:

✅ Runs inside headless Blender (`-b` mode)  
✅ Consumes commands from Redis Streams  
✅ Executes operations via Blender Python API  
✅ Returns structured responses with metrics  
✅ Supports idempotency, retries, and tracing  
✅ Scales horizontally (multiple workers)  

---

## Key Features

### 🎯 Minimal Surface
Only primitives for Blender data manipulation, evaluation, and export. No domain logic.

### 🔄 Deterministic & Idempotent
Every command accepts an `idempotency_key`. Safe to retry.

### ⚡ Efficient I/O
- Compact JSON/MessagePack payloads
- Optional Zstandard compression
- Large blobs by reference (file paths)

### 📊 Observable
- Rich, structured errors
- Per-command metrics
- Trace/span IDs
- Progress events

### 🔒 Secure
- Path allowlists
- Resource limits
- No arbitrary code execution

### 📈 Scalable
- Multiple workers via consumer groups
- Backpressure-safe (Redis Streams)
- Crash recovery (unacked messages re-delivered)

---

## Quick Start

Get started in 5 minutes:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# 3. Run sidecar
blender -b --python sidecar.py

# 4. Test (new terminal)
python tests/test_ping.py
```

See **[QUICKSTART.md](./QUICKSTART.md)** for detailed instructions.

---

## Documentation

### Core Documentation
- **[SPEC.md](./SPEC.md)** — Full specification (design principles, commands, schemas)
- **[ROADMAP.md](./ROADMAP.md)** — Implementation roadmap with milestones
- **[CONFIGURATION.md](./CONFIGURATION.md)** — Configuration guide (env vars, TOML, limits)
- **[QUICKSTART.md](./QUICKSTART.md)** — Get started in 5 minutes

### AI Integration (MCP)
- **[MCP_INTEGRATION_ANALYSIS.md](./MCP_INTEGRATION_ANALYSIS.md)** — Full analysis of MCP integration approaches
- **[MCP_QUICK_REFERENCE.md](./MCP_QUICK_REFERENCE.md)** — Code patterns and snippets for MCP implementation

### Technical Deep Dives
- **[THREADING.md](./THREADING.md)** — Threading model and safety
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** — Directory structure and conventions
- **[IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)** — Current implementation status

---

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Orchestrator│ XADD    │    Redis     │ XREAD   │   Blender   │
│  (Client)   ├────────>│   Streams    │<────────┤   Sidecar   │
│             │         │              │         │             │
│             │<────────┤ blender:cmd  ├────────>│ sidecar.py  │
│             │  XREAD  │ blender:reply│  XADD   │   + bpy     │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Why Redis Streams?

- **Reliability**: Ack/replay semantics
- **Backpressure**: Natural flow control
- **Multi-consumer**: Scale horizontally
- **Ordering**: Per-stream ordering guaranteed
- **Durability**: Persistent message log

---

## Command Set (Planned)

### Session & Health
- `Ping` ✅ — Health check / echo
- `GetCapabilities` — Feature discovery
- `Heartbeat` — Worker health updates

### Scene Management
- `CreateScene` — Create new scene
- `SaveBlend` — Save to .blend file
- `LoadBlend` — Link/load assets
- `PurgeOrphans` — Clean unused data

### Collections & Objects
- `CreateCollection` — New collection
- `InstanceCollection` — Single instance
- `InstanceCollectionMany` — Batch instancing
- `SetCustomProps` — Custom properties

### Geometry Nodes
- `AttachNodeGroup` — Add GN modifier
- `SetNodeParams` — Update GN inputs
- `SetNamedAttributes` — Push attributes

### Evaluation
- `EvaluateDepsgraph` — Force evaluation
- `RealizeInstances` — Convert to meshes

### Export
- `ExportGLTF` — Export to .glb file
- `WriteManifest` — Generate metadata JSON
- `ImportGLB` — Import external assets

### Utilities
- `Batch` — Execute multiple commands atomically
- `GetSceneSummary` — Counts, memory, AABB
- `CleanupTemp` — Remove temp files

---

## Message Schema

### Request
```json
{
  "v": "1.0",
  "trace_id": "uuid",
  "span_id": "uuid",
  "idempotency_key": "uuid-or-hash",
  "cmd": "Ping",
  "params": { "echo": "hello" },
  "opts": {
    "timeout_ms": 60000,
    "reply_stream": "blender:reply"
  }
}
```

### Response
```json
{
  "v": "1.0",
  "trace_id": "uuid",
  "span_id": "uuid",
  "status": "ok",
  "cmd": "Ping",
  "result": { "echo": "hello", "blender_version": "4.2.0" },
  "metrics": {
    "cpu_ms": 2,
    "wall_ms": 5,
    "mem_mb": 512
  }
}
```

---

## Example: Complete Dungeon Export

```python
# Pseudo-code (orchestrator side)

# 1. Create scene
CreateScene(name="dgn_042")

# 2. Load asset pack
LoadBlend(
    filepath="/assets/rooms.blend",
    link=True,
    collections=["COL_RoomRect", "COL_Door"]
)

# 3. Instance rooms
InstanceCollectionMany(
    parent_collection="ROOMS",
    items=[
        {"collection": "COL_RoomRect", "name": "r0", "transform": {...}},
        {"collection": "COL_RoomRect", "name": "r1", "transform": {...}},
        # ... 100 more rooms
    ]
)

# 4. Evaluate & export
EvaluateDepsgraph()
ExportGLTF(filepath="/build/dgn_042.glb", selection=["ROOMS"])
WriteManifest(filepath="/build/dgn_042.manifest.json")
```

---

## Development Status

### ✅ Milestone 0: Hello World (Current)
- [x] Project structure
- [x] Redis Streams consumer
- [x] Command router
- [x] Ping command
- [x] Configuration system
- [x] Documentation

### 🚧 Milestone 1: Core Commands (In Progress)
- [ ] `CreateScene`
- [ ] `LoadBlend`
- [ ] `InstanceCollection`
- [ ] `ExportGLTF`
- [ ] `WriteManifest`

See **[ROADMAP.md](./ROADMAP.md)** for full plan.

---

## Configuration

### Environment Variables (Recommended)

```bash
# .env
REDIS_URL=redis://localhost:6379/0
SIDECAR_WORKER_ID=worker-01
SIDECAR_LOG_LEVEL=DEBUG
PATHS_ASSETS_ROOT=./assets
PATHS_BUILD_ROOT=./build
```

### TOML Configuration

```toml
# sidecar_config.toml
[redis]
url = "redis://localhost:6379/0"
cmd_stream = "blender:cmd"

[sidecar]
worker_id = "worker-01"
log_level = "DEBUG"
```

See **[CONFIGURATION.md](./CONFIGURATION.md)** for full reference.

---

## Production Deployment

### Docker

```dockerfile
FROM ubuntu:22.04

# Install Blender
RUN apt-get update && apt-get install -y blender

# Copy sidecar
COPY sidecar.py /app/
COPY sidecar/ /app/sidecar/
COPY requirements.txt /app/

# Install deps
RUN blender --background --python-exec python3 -m pip install -r /app/requirements.txt

# Run
CMD ["blender", "-b", "--python", "/app/sidecar.py"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blender-sidecar
spec:
  replicas: 10  # Scale horizontally
  selector:
    matchLabels:
      app: blender-sidecar
  template:
    spec:
      containers:
      - name: sidecar
        image: blender-sidecar:1.0
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: REDIS_CONSUMER_GROUP
          value: "cg:prod"
```

---

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Start Redis + sidecar
docker-compose up -d

# Run tests
python tests/test_ping.py
```

### Golden Tests
```bash
# Ensure deterministic exports
pytest tests/golden/
```

---

## Performance

| Metric | Target |
|--------|--------|
| Latency (Ping) | P50 < 10ms, P99 < 50ms |
| Throughput | 100+ cmd/sec per worker |
| Export (1000 rooms) | < 10s |
| Memory | Stable over 24h soak test |

---

## Security

🔒 **Production Checklist**:
- [ ] Redis AUTH enabled (`redis://:password@...`)
- [ ] TLS for Redis (`rediss://...`)
- [ ] Path allowlists configured
- [ ] Resource limits set
- [ ] UI operators disabled (`allow_ops_fallback=false`)
- [ ] Network isolation (VPC/firewall)

---

## Contributing

1. Read **[SPEC.md](./SPEC.md)** for design principles
2. Pick a command from **[ROADMAP.md](./ROADMAP.md)**
3. Implement handler in `sidecar/commands/`
4. Add tests
5. Submit PR

---

## License

See [COPYING](../../COPYING) for Blender license.

Sidecar code: MIT License (or match Blender's GPL if integrated)

---

## Support

- **Documentation**: `docs/sidecar/`
- **Examples**: `tests/`
- **Issues**: GitHub Issues
- **Discord**: [Blender Dev Discord](https://blender.chat)

---

**Built with ❤️ for procedural worldgen, game pipelines, and headless automation.**

