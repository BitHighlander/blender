# Lessons Learned - Building Blender from Source

**Project**: Degenerate Labs Blender Fork  
**Timeline**: October 4-5, 2025  
**Goal**: Build custom Blender with first-class MCP/Redis integration  

---

## 🏗️ Building Blender

### What We Learned

1. **Blender uses CMake + Makefile wrapper**
   - Makefile is just a convenience wrapper
   - Real build system is CMake + Ninja (or Make)
   - Build output: `../build_darwin/` (one level up from source)

2. **Dependencies are HUGE (~973 MB)**
   - Pre-compiled libraries in `lib/macos_arm64/`
   - Must be git submodule or manual clone
   - Can't use `make update` on fresh clone (git submodule issues)
   - Solution: `git clone --depth=1 https://projects.blender.org/blender/lib-macos_arm64.git lib/macos_arm64`

3. **Incremental builds are FAST**
   - First build: ~30-60 minutes
   - Incremental: **3-4 seconds** with Ninja!
   - Developer mode: Optimized for fast rebuilds

4. **Build Modes**
   ```bash
   make lite        # Minimal features, fast
   make full        # All features
   make developer   # Best for development (fast rebuilds, tests)
   make release     # Production (matches official builds)
   make ninja       # Use Ninja (faster than Make)
   make ccache      # Cache for even faster rebuilds
   ```

5. **Combining modes is powerful**
   ```bash
   make developer ninja  # Our choice: fast + full features
   ```

---

## 🧵 Critical Threading Discovery

### The Problem: Blender's Main Thread

**Blender's Python is NOT thread-safe!**

From `doc/python_api/rst/info_gotchas_threading.rst`:
> "Python threads cause Blender to crash in hard to diagnose ways"

### What Went Wrong Initially

Our first sidecar implementation:
```python
# ❌ WRONG: Blocks main thread
def run(self):
    while self.running:
        messages = self.redis_client.xreadgroup(...)  # BLOCKS HERE!
        self.router.route(cmd, params)  # Freezes viewport!
```

**Problem**: 
- Main thread stuck waiting for Redis
- Viewport freezes
- No real-time updates
- Blender appears hung

### The Solution: Background Thread + bpy.app.timers

**Pattern learned from blender-mcp by ahujasid:**

```python
# ✅ CORRECT: Non-blocking execution

# 1. Background thread polls I/O
self.server_thread = threading.Thread(
    target=self._server_loop,
    daemon=True  # Won't block Blender exit
)
self.server_thread.start()

# 2. Queue execution in main thread
def _queue_command(self, command):
    def execute_in_main_thread():
        self.execute_command(command)
        return None  # Run once
    
    # THE MAGIC: Execute in Blender's main thread when ready
    bpy.app.timers.register(execute_in_main_thread, first_interval=0.0)
```

**Result**:
- ✅ Background thread: Handles I/O (sockets, Redis, HTTP)
- ✅ Main thread: Stays responsive, processes queued commands
- ✅ Viewport: Updates in real-time!

### Key Functions

**`bpy.app.timers.register(function, first_interval=0.0)`**
- Queues function to run in main thread
- `first_interval=0.0` = run ASAP (next frame)
- Return `None` = run once (not persistent)
- Implemented in C: `source/blender/python/intern/bpy_app_timers.cc`

---

## 🔌 MCP Socket Server Architecture

### How It Works

```
┌─────────────┐
│  MCP Client │ (Node.js, Cursor, etc)
└──────┬──────┘
       │ Socket connection
       │ localhost:9876
       │
┌──────▼──────────────────────────┐
│  Background Thread              │
│  (Socket server accepts         │
│   connections, reads data)      │
└──────┬──────────────────────────┘
       │
       │ bpy.app.timers.register()
       │
┌──────▼──────────────────────────┐
│  Main Thread (Blender)          │
│  - Executes commands            │
│  - Updates viewport             │
│  - Renders scene                │
│  - Sends responses back         │
└─────────────────────────────────┘
```

### Message Flow

1. **Client connects** to socket (localhost:9876)
2. **Client sends JSON command**:
   ```json
   {
     "type": "create_cube",
     "params": {"location": [0, 0, 2], "size": 1}
   }
   ```
3. **Background thread receives** command
4. **Queues via bpy.app.timers** for main thread
5. **Main thread executes** when ready
6. **Response sent** back to client:
   ```json
   {
     "status": "success",
     "result": {"name": "Cube.001", "location": [0, 0, 2]}
   }
   ```

### Why This Works

- **No blocking**: Background thread handles network I/O
- **Thread-safe**: Only main thread touches bpy
- **Responsive**: Viewport updates while processing
- **Simple**: Just sockets, no complex protocols

---

## 📦 First-Class vs Addon

### What "First-Class" Means

**Addon approach** (blender-mcp original):
- User must enable in Preferences
- Checkbox in Add-ons menu
- Can be disabled/broken
- Feels like a plugin

**First-class approach** (our implementation):
- Runs automatically on Blender startup
- No checkbox needed
- Part of Blender itself
- In `scripts/startup/` (auto-executed)
- Can't be accidentally disabled

### How We Made It First-Class

1. **Location**: `scripts/startup/bl_mcp_server.py`
   - Blender automatically runs all scripts in `startup/`
   - No manual enable needed

2. **Auto-start with timer**:
   ```python
   def register():
       bpy.app.timers.register(start_mcp_server, first_interval=2.0)
   
   # Auto-register
   if __name__ != "__main__":
       register()
   ```

3. **Built into source tree**:
   - Not in `addons/`, in `startup/`
   - Gets compiled/installed with Blender
   - Part of the build

---

## 🔄 Redis vs MCP Architecture

### Current State

**MCP Server** (Working):
- Protocol: Socket (TCP, port 9876)
- Client: Direct socket connection
- Message: JSON over socket
- Pattern: Request → Response
- Integration: First-class, auto-starts

**Redis Sidecar** (Has threading fix):
- Protocol: Redis Streams
- Client: Redis XREAD/XADD
- Message: JSON in stream payload
- Pattern: Pub/Sub with acknowledgment
- Integration: Run with `--python sidecar.py`

### Key Difference

| Aspect | MCP Socket | Redis Sidecar |
|--------|-----------|---------------|
| **Connection** | Direct socket | Via Redis server |
| **Clients** | Single/few | Distributed workers |
| **Deployment** | Same machine | Multi-machine |
| **Complexity** | Simple | More complex |
| **Scaling** | Limited | Horizontal |
| **Use Case** | AI agents, direct control | Backend automation, workers |

---

## 🎓 Technical Insights

### 1. bpy.context in Headless Mode

**Problem**: `bpy.context.active_object` doesn't work well in headless/script mode

**Solution**: Always use fallbacks
```python
# Get active object safely
obj = bpy.context.view_layer.objects.active or bpy.context.scene.objects[-1]

# Or create your own context
scene = bpy.context.scene
view_layer = bpy.context.view_layer
```

### 2. Collection Management

**Problem**: Can't unlink object from collection it's not in

**Solution**: Check first
```python
if obj.name in scene.collection.objects:
    scene.collection.objects.unlink(obj)
```

### 3. Python Module Loading

**Blender's Python looks in**:
1. `scripts/modules/` (built-in modules)
2. `scripts/startup/` (auto-run on startup)
3. `scripts/addons/` (user addons)
4. System Python paths

**Our sidecar** went in `scripts/modules/sidecar/`

**Our MCP server** went in `scripts/startup/bl_mcp_server.py`

### 4. Build System Gotchas

**CMake doesn't auto-detect new files!**
- Adding files to `scripts/` requires rebuild
- CMake cache might need clearing
- Incremental builds copy changed files
- Manual copy during development: OK

**Quick iteration**:
```bash
# During development
cp my_script.py ../build_darwin/bin/Blender.app/Contents/Resources/5.0/scripts/startup/

# For production
make developer ninja  # Only 3-4 seconds!
```

### 5. Git LFS with Forks

**Problem**: GitHub forks can't upload new LFS objects

**Solution**: 
```bash
# Always push with --no-verify
git push degen master-degen --no-verify

# Config option
git config lfs.pushTransfer false
```

---

## 🛠️ Development Workflow

### Daily Iteration

1. **Make changes** to source files
2. **Quick rebuild**: `make developer ninja` (3-4s)
3. **Test**: Run Blender
4. **Commit**: `git commit -m "..."`
5. **Push**: `git push degen master-degen --no-verify`

### Testing MCP

1. **Start Blender**: `open ../build_darwin/bin/Blender.app`
2. **Wait 2 seconds** (MCP auto-starts)
3. **Test**: `node test_mcp_direct.mjs`
4. **Watch**: Blender window for real-time updates!

---

## 💡 Key Takeaways

### 1. Thread Safety is Critical
**Never call bpy from background threads!**
- Use `bpy.app.timers.register()` to queue for main thread
- Always make I/O threads `daemon=True`
- Short `time.sleep()` intervals keep things responsive

### 2. Simple is Better
- Socket server: 200 lines, works perfectly
- Complex protocols: Not needed for this use case
- Proven patterns: Copy what works (blender-mcp)

### 3. First-Class Integration Rocks
- Auto-start = no user config needed
- Built-in = can't be broken by user
- Startup scripts = run every time

### 4. Fast Builds Enable Iteration
- Ninja + ccache: Crucial for development
- 3-4 second rebuilds: Can iterate quickly
- Developer mode: Worth it!

---

## 🎯 What Works Right Now

Run this to see it all in action:

```bash
# 1. Start Blender (GUI or headless)
open ../build_darwin/bin/Blender.app

# 2. Wait 2 seconds for MCP to auto-start

# 3. Test it!
node test_mcp_direct.mjs

# You should see:
# ✅ Connected to Blender MCP server
# ✅ Ping successful
# ✅ Scene info retrieved
# ✅ Cube created in Blender!
```

**The cube APPEARS in Blender in REAL-TIME!**

---

## 📖 Resources Created

### Documentation
- `BUILD_GUIDE.md` - Complete build instructions
- `LEARNING_NOTES.md` - Learning journal
- `GIT_WORKFLOW.md` - Git commands for fork
- `MCP_INTEGRATION.md` - MCP architecture
- `STATUS.md` - Current state
- `docs/sidecar/THREADING.md` - Threading deep-dive
- `LESSONS_LEARNED.md` - This document

### Code
- `scripts/startup/bl_mcp_server.py` - First-class MCP server
- `sidecar/` - Redis bridge (with threading fix)
- `test_mcp_direct.mjs` - MCP test
- `test_mcp_socket.py` - Socket test

### Tools
- `start_sidecar_gui.sh` - Start Blender with sidecar
- `GNUmakefile` - Already there, we used it!

---

## 🔮 Next Phase: Redis Bridge

**Goal**: Make Redis Sidecar match MCP's flexibility

**Approach**: Feature-for-feature parity with MCP socket server

See: `REDIS_BRIDGE_PLAN.md` (next document)

---

**Bottom Line**: We built Blender, fixed threading, integrated MCP, and it WORKS! 🚀

