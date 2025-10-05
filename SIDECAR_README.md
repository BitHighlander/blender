# 🎨 Blender Python Sidecar

> A production-ready Redis bridge for headless Blender automation

This directory contains a **Blender Python Sidecar** — a minimal service that runs inside headless Blender and exposes the Blender Python API over Redis Streams.

---

## What is it?

A thin bridge between your orchestrator (game server, worldgen pipeline, etc.) and Blender's Python API. Perfect for:

- 🏰 Procedural worldgen (dungeons, terrains, buildings)
- 🎮 Game asset pipelines
- 🤖 Headless Blender automation
- 📦 Batch export workflows
- 🔧 API-driven scene manipulation

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 3. Run sidecar
blender -b --python sidecar.py

# 4. Test (new terminal)
python tests/test_ping.py
```

Expected output:
```
✅ Response received!
Echo: Hello from test script!
Blender: 4.2.0
Status: ok
```

---

## Documentation

📚 **All documentation is in `docs/sidecar/`**

Start here:
- **[README.md](docs/sidecar/README.md)** — Overview & features
- **[QUICKSTART.md](docs/sidecar/QUICKSTART.md)** — Get started in 5 minutes
- **[SPEC.md](docs/sidecar/SPEC.md)** — Complete specification
- **[ROADMAP.md](docs/sidecar/ROADMAP.md)** — Implementation plan
- **[CONFIGURATION.md](docs/sidecar/CONFIGURATION.md)** — Configuration guide

---

## Current Status

✅ **Milestone 0: Hello World** (Complete)

Working:
- Redis Streams consumer
- Command routing
- `Ping` command
- Configuration system
- Comprehensive documentation

Next:
- Milestone 1: Core commands (`CreateScene`, `ExportGLTF`, etc.)

See [ROADMAP.md](docs/sidecar/ROADMAP.md) for details.

---

## Architecture

```
Orchestrator → Redis Streams → Blender Sidecar → bpy
               (blender:cmd)    (sidecar.py)      (Blender API)
               
               (blender:reply) ← Response
```

---

## Key Features

✅ **Idempotent** — Safe to retry any command  
✅ **Observable** — Structured errors, metrics, tracing  
✅ **Scalable** — Multiple workers via consumer groups  
✅ **Secure** — Path allowlists, resource limits  
✅ **Efficient** — Optional compression, batch operations  

---

## Example: Ping Command

**Send command:**
```bash
redis-cli XADD blender:cmd "*" payload '{
  "v": "1.0",
  "cmd": "Ping",
  "params": {"echo": "Hello!"},
  "trace_id": "test-001"
}'
```

**Read response:**
```bash
redis-cli XREAD STREAMS blender:reply 0
```

**Response:**
```json
{
  "status": "ok",
  "cmd": "Ping",
  "result": {
    "echo": "Hello!",
    "blender_version": "4.2.0",
    "worker_id": "my-laptop"
  },
  "metrics": {
    "cpu_ms": 2,
    "wall_ms": 5
  }
}
```

---

## Project Structure

```
blender/
├── sidecar.py              # Entry point
├── sidecar/                # Main package
│   ├── config.py           # Configuration
│   ├── consumer.py         # Redis consumer
│   ├── router.py           # Command router
│   ├── errors.py           # Error handling
│   ├── telemetry.py        # Logging & metrics
│   └── commands/           # Command handlers
│       └── ping.py         # Ping command
├── tests/
│   └── test_ping.py        # Test script
├── docs/sidecar/           # Documentation
└── requirements.txt        # Dependencies
```

See [PROJECT_STRUCTURE.md](docs/sidecar/PROJECT_STRUCTURE.md) for details.

---

## Development

**Add a new command:**

1. Create handler: `sidecar/commands/my_command.py`
2. Implement: `handle_my_command(config, params, opts) -> dict`
3. Register: Add to `sidecar/router.py`
4. Test: Create `tests/test_my_command.py`
5. Document: Update `docs/sidecar/SPEC.md`

See [ROADMAP.md](docs/sidecar/ROADMAP.md) for command priorities.

---

## Production Deployment

**Docker:**
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y blender
COPY sidecar.py sidecar/ requirements.txt /app/
RUN pip install -r /app/requirements.txt
CMD ["blender", "-b", "--python", "/app/sidecar.py"]
```

**Scale with multiple workers:**
```bash
# Start 10 workers (Docker Compose)
docker-compose up --scale sidecar=10
```

See [CONFIGURATION.md](docs/sidecar/CONFIGURATION.md) for deployment examples.

---

## Support

- **Docs**: `docs/sidecar/`
- **Examples**: `tests/`
- **Questions**: File a GitHub issue

---

## License

This sidecar code is independent of Blender core. See project root for Blender's license.

---

**Built for:** Procedural worldgen, game pipelines, and headless automation  
**Status:** Ready for development (Milestone 0 complete)  
**Next:** Implement core commands (Milestone 1)

🚀 **Get started:** `docs/sidecar/QUICKSTART.md`

