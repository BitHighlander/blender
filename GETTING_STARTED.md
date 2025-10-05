# 🚀 Getting Started with Blender Sidecar

Welcome! This is your **5-minute quick start** to get the Blender Python Sidecar running.

## What is this?

A Redis-based command bridge for headless Blender automation. Perfect for:
- 🏰 Procedural worldgen (dungeons, terrains)
- 🎮 Game asset pipelines
- 🤖 Headless Blender automation

## Quick Start (5 minutes)

### 1. Start Redis
```bash
docker run -d -p 6379:6379 --name redis-sidecar redis:7-alpine
```

### 2. Install Dependencies
```bash
pip install redis python-dotenv
```

### 3. Run Sidecar
```bash
blender -b --python sidecar.py
```

You should see:
```
🎨 Blender Python Sidecar - Redis Bridge
✅ Blender 4.2.0 detected
🚀 Sidecar ready! Waiting for commands...
```

### 4. Test It (new terminal)
```bash
python tests/test_ping.py
```

Expected output:
```
✅ Response received!
Echo: Hello from test script!
Blender: 4.2.0
Status: ok
⏱️  Metrics: CPU Time: 2 ms, Wall Time: 5 ms
```

## 🎉 Success!

You now have a working Blender sidecar that can:
- ✅ Accept commands over Redis Streams
- ✅ Execute Blender operations
- ✅ Return structured responses with metrics

## Next Steps

### Learn More
- **Full Docs**: `docs/sidecar/README.md`
- **Quick Start Guide**: `docs/sidecar/QUICKSTART.md`
- **Complete Spec**: `docs/sidecar/SPEC.md`
- **Roadmap**: `docs/sidecar/ROADMAP.md`

### Test Manually
```bash
# Send command via redis-cli
redis-cli XADD blender:cmd "*" payload '{"v":"1.0","cmd":"Ping","params":{"echo":"Hello!"}}'

# Read response
redis-cli XREAD STREAMS blender:reply 0
```

### Implement More Commands
See `docs/sidecar/ROADMAP.md` for Milestone 1:
- `CreateScene` — Create Blender scenes
- `LoadBlend` — Load asset packs
- `InstanceCollection` — Place instances
- `ExportGLTF` — Export to .glb files

## Need Help?

- **Documentation**: `docs/sidecar/`
- **Examples**: `tests/`
- **Configuration**: `docs/sidecar/CONFIGURATION.md`

---

**Built for:** Procedural worldgen & game pipelines  
**Status:** Milestone 0 Complete ✅
