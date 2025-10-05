# Project Structure

Overview of the Blender Sidecar project files and organization.

---

## Directory Layout

```
blender/
├── docs/sidecar/              # Documentation
│   ├── README.md              # Main documentation
│   ├── SPEC.md                # Complete specification
│   ├── ROADMAP.md             # Implementation roadmap
│   ├── CONFIGURATION.md       # Configuration guide
│   ├── QUICKSTART.md          # Getting started guide
│   └── PROJECT_STRUCTURE.md   # This file
│
├── sidecar/                   # Main package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration loader
│   ├── consumer.py            # Redis Streams consumer
│   ├── router.py              # Command dispatcher
│   ├── errors.py              # Error codes & exceptions
│   ├── telemetry.py           # Logging & metrics
│   └── commands/              # Command handlers
│       ├── __init__.py
│       └── ping.py            # Ping command handler
│
├── tests/                     # Test scripts
│   └── test_ping.py           # Ping command test
│
├── sidecar.py                 # Main entry point
├── requirements.txt           # Python dependencies
├── env.example                # Example environment config
└── sidecar_config.toml        # Example TOML config
```

---

## Core Files

### Entry Point

#### `sidecar.py`
Main entry point for the sidecar. Run with:
```bash
blender -b --python sidecar.py
```

Responsibilities:
- Load configuration
- Setup logging
- Initialize Blender environment
- Start Redis consumer
- Handle graceful shutdown

---

## Package Files (`sidecar/`)

### `__init__.py`
Package initialization. Exports main classes and functions.

### `config.py`
Configuration management:
- Load defaults
- Merge TOML config
- Merge .env file
- Override with environment variables

Supports:
- Development defaults (localhost Redis)
- Production configuration
- Flexible override hierarchy

### `consumer.py`
Redis Streams consumer:
- Connect to Redis
- Create/join consumer group
- Read commands (blocking with timeout)
- Route to command handlers
- Send responses
- Acknowledge messages

Features:
- Automatic reconnection
- Graceful shutdown
- Message replay on crash

### `router.py`
Command routing:
- Maintain command registry
- Route commands to handlers
- Catch and wrap errors
- Support dynamic handler registration

### `errors.py`
Error handling:
- Standard error codes (E_xxx)
- Structured error responses
- Retryability flags
- Rich context/details

Error classes:
- `SidecarError` (base)
- `CommandError`
- `ValidationError`
- `TimeoutError`
- `SceneNotFoundError`
- `CollectionNotFoundError`
- `ExportError`
- `UnsupportedVersionError`

### `telemetry.py`
Observability:
- Structured logging
- Metrics collection (CPU, wall time, memory)
- Response envelope creation
- Startup info logging

Future:
- Event emission to Redis
- Health heartbeats
- Distributed tracing

---

## Command Handlers (`sidecar/commands/`)

Each command is a separate module with a `handle_*` function.

### Command Handler Signature

```python
def handle_command(
    config: Dict[str, Any],
    params: Dict[str, Any],
    opts: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle a command.
    
    Args:
        config: Sidecar configuration
        params: Command parameters
        opts: Command options (timeout, reply_stream, etc.)
    
    Returns:
        Result dictionary
    
    Raises:
        SidecarError: On command failure
    """
    pass
```

### Implemented Commands

#### `ping.py` — Ping ✅
Simple health check that echoes a message.

Parameters:
- `echo` (string, optional): Message to echo back

Returns:
- `echo`: Echoed message
- `blender_version`: Blender version string
- `sidecar_version`: Sidecar version
- `worker_id`: Worker identifier
- `hostname`: System hostname

---

## Configuration Files

### `env.example`
Example environment configuration. Copy to `.env`:
```bash
cp env.example .env
```

Includes:
- Redis connection
- Worker ID
- Log level
- Paths
- Feature flags
- Resource limits

### `sidecar_config.toml`
Example TOML configuration. Alternative to env vars.

Sections:
- `[redis]` — Redis connection & streams
- `[sidecar]` — Worker settings
- `[paths]` — File paths & allowlists
- `[features]` — Feature flags
- `[limits]` — Resource limits
- `[blender]` — Blender settings

---

## Dependencies (`requirements.txt`)

### Required
- `redis>=5.0.0` — Redis client
- `python-dotenv>=1.0.0` — .env file support

### Optional
- `toml>=0.10.2` — TOML config (recommended)
- `zstandard>=0.22.0` — Compression
- `msgpack>=1.0.7` — Binary serialization
- `psutil>=5.9.0` — Memory/CPU metrics

### Development
- `pytest` — Testing framework
- `black` — Code formatting
- `ruff` — Linting

---

## Test Files (`tests/`)

### `test_ping.py`
Interactive test script for Ping command.

Usage:
```bash
# Default (localhost Redis)
python tests/test_ping.py

# Custom Redis URL
python tests/test_ping.py redis://host:6379/0

# Custom echo message
python tests/test_ping.py redis://localhost:6379/0 "Hello!"
```

Features:
- Sends Ping command
- Waits for response (10s timeout)
- Pretty-prints result
- Shows metrics
- Error handling

---

## Documentation Files (`docs/sidecar/`)

### `README.md`
Main documentation:
- Overview
- Quick start
- Architecture
- Command reference
- Configuration summary
- Deployment examples

### `SPEC.md`
Complete specification:
- Design principles
- Runtime model
- Redis topology
- Message schemas
- Full command set
- Error model
- Performance
- Observability
- Security
- Configuration
- Testing strategy
- Operational playbook

### `ROADMAP.md`
Implementation roadmap:
- 7 milestones (Milestone 0 complete)
- Testable deliverables
- Success criteria
- Time estimates
- Testing strategy
- Progress tracking

### `CONFIGURATION.md`
Configuration guide:
- Configuration sources
- Environment variables
- TOML reference
- Example setups
- Docker/Kubernetes examples
- Validation
- Security best practices

### `QUICKSTART.md`
Getting started (5 minutes):
- Prerequisites
- Installation
- Start Redis
- Run sidecar
- Send test command
- Read response
- Troubleshooting
- Next steps

### `PROJECT_STRUCTURE.md`
This file — project organization and file overview.

---

## Development Workflow

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy config
cp env.example .env
```

### 2. Start Services
```bash
# Terminal 1: Redis
docker run -d -p 6379:6379 redis:7-alpine

# Terminal 2: Sidecar
blender -b --python sidecar.py
```

### 3. Test
```bash
# Terminal 3: Test
python tests/test_ping.py
```

### 4. Add Commands
```bash
# 1. Create handler: sidecar/commands/new_command.py
# 2. Register in: sidecar/router.py
# 3. Test: tests/test_new_command.py
# 4. Document: docs/sidecar/SPEC.md
```

---

## File Size Summary

| File | Lines | Purpose |
|------|-------|---------|
| `sidecar.py` | ~80 | Entry point |
| `sidecar/config.py` | ~200 | Configuration |
| `sidecar/consumer.py` | ~200 | Redis consumer |
| `sidecar/router.py` | ~80 | Command routing |
| `sidecar/errors.py` | ~100 | Error handling |
| `sidecar/telemetry.py` | ~150 | Observability |
| `sidecar/commands/ping.py` | ~50 | Ping handler |
| `tests/test_ping.py` | ~150 | Ping test |
| **Total (code)** | **~1,000** | Implementation |
| **Docs** | **~2,000** | Documentation |

---

## Next Files to Create

As you implement more commands (Milestone 1+):

```
sidecar/commands/
├── scene.py              # CreateScene, SaveBlend, GetSceneSummary
├── collections.py        # CreateCollection, InstanceCollection
├── export.py             # ExportGLTF, WriteManifest
├── geometry_nodes.py     # AttachNodeGroup, SetNodeParams
└── batch.py              # Batch command

tests/
├── test_scene.py
├── test_collections.py
├── test_export.py
└── golden/               # Golden test fixtures
    ├── input_scene.blend
    └── expected_output.glb
```

---

## Key Design Decisions

### 1. Configuration Hierarchy
Environment variables > .env > TOML > defaults

Rationale: Flexibility for dev/staging/prod without code changes.

### 2. Redis Streams (not Pub/Sub)
Streams provide:
- Reliability (ack/replay)
- Backpressure
- Message history
- Consumer groups

### 3. Command = Module
Each command is a separate file for:
- Clear separation
- Easy testing
- Dynamic registration

### 4. Structured Errors
All errors have:
- Code (stable, symbolic)
- Message (human-readable)
- Details (context)
- Retryability flag

### 5. No bpy in Config/Consumer
Only command handlers use `bpy`. Config and consumer work without Blender for testing.

---

## Import Graph

```
sidecar.py
├── bpy (Blender API)
├── sidecar.config
├── sidecar.consumer
│   └── sidecar.router
│       └── sidecar.commands.*
│           └── bpy (only here)
├── sidecar.telemetry
└── sidecar.errors
```

---

## Conventions

### Naming
- Commands: PascalCase (e.g., `CreateScene`)
- Handlers: snake_case (e.g., `handle_create_scene`)
- Files: snake_case (e.g., `geometry_nodes.py`)
- Error codes: SCREAMING_SNAKE (e.g., `E_SCENE_NOT_FOUND`)

### Logging
- Use structured logging
- Include trace_id in all logs
- Levels: DEBUG (dev), INFO (prod), WARNING (recoverable), ERROR (failure)

### Response Format
Always include:
- `v` (version)
- `trace_id`
- `span_id`
- `status` (ok/error/partial)
- `cmd`
- `result` or `error`
- `metrics`

---

## Testing Checklist

For each new command:

- [ ] Handler implementation
- [ ] Unit test (mocked bpy)
- [ ] Integration test (real Blender)
- [ ] Documentation (SPEC.md)
- [ ] Example in QUICKSTART.md
- [ ] Error cases tested
- [ ] Metrics validated

---

## Deployment Checklist

Before production:

- [ ] Configuration validated
- [ ] Redis AUTH enabled
- [ ] TLS enabled
- [ ] Path allowlists set
- [ ] Resource limits configured
- [ ] Monitoring dashboard
- [ ] Alerting rules
- [ ] Runbook documentation
- [ ] Load testing completed
- [ ] Soak testing passed

---

## Useful Commands

```bash
# Check Redis streams
redis-cli XLEN blender:cmd
redis-cli XLEN blender:reply

# Monitor commands
redis-cli MONITOR

# List consumer groups
redis-cli XINFO GROUPS blender:cmd

# List consumers
redis-cli XINFO CONSUMERS blender:cmd cg:dev

# Pending messages
redis-cli XPENDING blender:cmd cg:dev

# Clear streams
redis-cli DEL blender:cmd blender:reply
```

---

## Resources

- **Blender Python API**: https://docs.blender.org/api/current/
- **Redis Streams**: https://redis.io/docs/data-types/streams/
- **redis-py**: https://redis-py.readthedocs.io/

---

**Last Updated:** October 5, 2025  
**Status:** Milestone 0 Complete ✅

