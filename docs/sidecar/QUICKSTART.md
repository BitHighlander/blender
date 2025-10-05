# Quick Start Guide

Get the Blender sidecar running in 5 minutes!

---

## Prerequisites

1. **Blender 4.2+** (with Python 3.11+)
2. **Redis 7+** (Docker or local)
3. **Python dependencies** (redis-py, python-dotenv)

---

## Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Or manually:

```bash
pip install redis python-dotenv
```

---

## Step 2: Start Redis

### Option A: Docker (Recommended)

```bash
docker run -d \
  --name redis-sidecar \
  -p 6379:6379 \
  redis:7-alpine
```

### Option B: Local Redis

```bash
# macOS (Homebrew)
brew install redis
redis-server

# Linux
sudo systemctl start redis

# Windows
# Download from: https://redis.io/download
```

---

## Step 3: Run the Sidecar

```bash
# Run with Blender in headless mode
blender -b --python sidecar.py
```

You should see output like:

```
============================================================
🎨 Blender Python Sidecar - Redis Bridge
============================================================
Version: 1.0.0-dev
Worker ID: your-hostname

✅ Blender 4.2.0 detected
   Build: darwin

📋 Configuration:
   Redis: redis://localhost:6379/0
   Command stream: blender:cmd
   Consumer group: cg:dev
   Log level: DEBUG

[INFO] 🚀 Sidecar ready! Waiting for commands...
[INFO] 📬 Command stream: blender:cmd
[INFO] 📤 Reply stream: blender:reply
[INFO] 👤 Worker ID: your-hostname
```

---

## Step 4: Send a Test Command (Ping)

Open a new terminal and use `redis-cli`:

```bash
# Send a Ping command
redis-cli XADD blender:cmd "*" payload '{
  "v": "1.0",
  "cmd": "Ping",
  "params": {"echo": "Hello, Blender!"},
  "trace_id": "test-001",
  "span_id": "span-001"
}'
```

Expected output in sidecar terminal:

```
[DEBUG] Received message 1728123456789-0: Ping
[DEBUG] Routing command: Ping
[INFO] ✅ Command succeeded: Ping (trace=test-001)
[DEBUG] Sent response to blender:reply
[DEBUG] Acknowledged message: 1728123456789-0
```

---

## Step 5: Read the Response

```bash
# Read response from reply stream
redis-cli XREAD STREAMS blender:reply 0
```

Expected output:

```json
1) 1) "blender:reply"
   2) 1) 1) "1728123456790-0"
         2) 1) "payload"
            2) "{
              \"v\": \"1.0\",
              \"trace_id\": \"test-001\",
              \"span_id\": \"span-001\",
              \"status\": \"ok\",
              \"cmd\": \"Ping\",
              \"result\": {
                \"echo\": \"Hello, Blender!\",
                \"blender_version\": \"4.2.0\",
                \"sidecar_version\": \"1.0.0-dev\",
                \"worker_id\": \"your-hostname\",
                \"hostname\": \"your-hostname\",
                \"blender_build\": \"darwin\"
              },
              \"metrics\": {
                \"cpu_ms\": 2,
                \"wall_ms\": 5,
                \"mem_mb\": 0,
                \"depsgraph_updates\": 0
              }
            }"
```

---

## Troubleshooting

### Sidecar won't start

**Problem:** `ModuleNotFoundError: No module named 'redis'`

**Solution:** Blender uses its own Python. Install dependencies in Blender's Python:

```bash
# Find Blender's Python
blender --background --python-expr "import sys; print(sys.executable)"

# Install to Blender's Python (macOS example)
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install redis python-dotenv
```

### Can't connect to Redis

**Problem:** `Failed to connect to Redis: Error 61 connecting to localhost:6379. Connection refused.`

**Solution:** Make sure Redis is running:

```bash
# Check if Redis is running
redis-cli ping
# Expected: PONG

# If not running, start it (Docker)
docker start redis-sidecar
```

### No commands received

**Problem:** Sidecar starts but doesn't receive commands

**Solution:** Check that the stream/group names match:

```bash
# List streams
redis-cli KEYS blender:*

# Check consumer group
redis-cli XINFO GROUPS blender:cmd
```

---

## Next Steps

### Test with Python Script

Create `tests/test_ping.py`:

```python
#!/usr/bin/env python3
import redis
import json
import time
import uuid

# Connect to Redis
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Send Ping command
trace_id = str(uuid.uuid4())
request = {
    "v": "1.0",
    "cmd": "Ping",
    "params": {"echo": "Hello from Python!"},
    "trace_id": trace_id,
    "span_id": str(uuid.uuid4()),
}

print(f"Sending Ping command (trace={trace_id})...")
r.xadd("blender:cmd", {"payload": json.dumps(request)})

# Wait for response
print("Waiting for response...")
time.sleep(1)

# Read response
messages = r.xread({"blender:reply": "0"}, count=10)
for stream, message_list in messages:
    for msg_id, msg_data in message_list:
        payload = json.loads(msg_data["payload"])
        if payload.get("trace_id") == trace_id:
            print("\n✅ Response received:")
            print(json.dumps(payload, indent=2))
            break
```

Run it:

```bash
python tests/test_ping.py
```

### Try More Commands

Once the basic Ping works, you can implement additional commands:

- `GetCapabilities` — discover available features
- `CreateScene` — create a new Blender scene
- `ExportGLTF` — export scene to GLB file

See `ROADMAP.md` for the implementation plan.

---

## Development Tips

### Enable Debug Logging

```bash
# Set in .env
SIDECAR_LOG_LEVEL=DEBUG

# Or as environment variable
SIDECAR_LOG_LEVEL=DEBUG blender -b --python sidecar.py
```

### Monitor Redis Streams

```bash
# Watch commands in real-time
redis-cli --csv XREAD BLOCK 0 STREAMS blender:cmd $

# Count messages
redis-cli XLEN blender:cmd
redis-cli XLEN blender:reply

# Clear streams (for testing)
redis-cli DEL blender:cmd blender:reply
```

### Test Without Blender (Limited)

For testing configuration/Redis connectivity:

```bash
# Run sidecar.py directly (no bpy commands will work)
python sidecar.py
```

---

## Configuration Options

See `CONFIGURATION.md` for full details on:

- Environment variables
- TOML configuration
- Path allowlists
- Feature flags
- Resource limits

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

---

## Performance Tips

1. **Multiple Workers**: Run multiple Blender processes for parallelism
2. **Batching**: Use `Batch` command to group operations
3. **Compression**: Enable zstd for large payloads (production)
4. **Persistent Redis**: Use RDB/AOF for durability

---

## Security Notes

🔒 **Development Setup (Current)**:
- Redis on localhost without authentication
- OK for local development

🔒 **Production Setup**:
- Use Redis AUTH: `redis://:password@host:port/db`
- Enable TLS: `rediss://...`
- Restrict network access
- Enable path allowlists
- Set resource limits

See `CONFIGURATION.md` for production setup.

---

## Getting Help

- **Documentation**: `docs/sidecar/`
- **Examples**: `tests/`
- **Issues**: File a GitHub issue
- **Logs**: Check sidecar terminal output

---

Congratulations! 🎉 You now have a working Blender sidecar that can respond to commands over Redis!

