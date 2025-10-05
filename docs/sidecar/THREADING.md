# Threading in Blender - Critical Architecture Pattern

## 🚨 The Problem: Blocking Blender's Main Thread

**Blender's Python integration is NOT thread-safe!** As documented in `doc/python_api/rst/info_gotchas_threading.rst`:

> **Python Threads are Not Supported**
> 
> In short: Python threads cause Blender to crash in hard to diagnose ways.

### Original (Broken) Approach

Our initial sidecar implementation ran a **blocking loop** in Blender's main thread:

```python
# ❌ WRONG: Blocks main thread, freezes viewport
def run(self):
    while self.running:
        messages = self.redis_client.xreadgroup(...)  # BLOCKS HERE
        self._process_message(msg)  # Executes directly
```

**Problem**: The main thread is stuck waiting for Redis messages, so:
- ❌ Viewport freezes
- ❌ UI doesn't update
- ❌ No real-time feedback
- ❌ Blender appears hung

---

## ✅ The Solution: Background Thread + bpy.app.timers

Inspired by [blender-mcp](https://github.com/ahujasid/blender-mcp), we use:

1. **Background daemon thread** - Polls Redis without blocking main thread
2. **`bpy.app.timers.register()`** - Queues commands for main thread execution

### New (Correct) Architecture

```python
# ✅ CORRECT: Non-blocking, responsive execution

# 1. Start background thread (doesn't block main thread)
def run(self):
    self.consumer_thread = threading.Thread(
        target=self._consumer_loop,
        daemon=True,  # Won't block Blender exit
    )
    self.consumer_thread.start()

# 2. Background thread polls Redis
def _consumer_loop(self):
    while self.running:
        messages = self.redis_client.xreadgroup(...)
        # Queue for main thread execution (doesn't execute here!)
        self._queue_message_for_execution(msg)

# 3. Queue execution in main thread using bpy.app.timers
def _queue_message_for_execution(self, message_id, message_data):
    def execute_in_main_thread():
        self._process_message(message_id, message_data)
        return None  # Don't repeat timer
    
    # THE MAGIC: Execute in Blender's main thread
    bpy.app.timers.register(execute_in_main_thread, first_interval=0.0)

# 4. Main thread processes commands when ready
def _process_message(self, message_id, message_data):
    # Executes in main thread via bpy.app.timers
    result = self.router.route(cmd, params, opts)
    # Viewport updates happen naturally!
```

---

## 🎯 Key Benefits

### Before (Blocking):
- 🔴 **Main thread**: Blocked waiting for Redis
- 🔴 **Viewport**: Frozen, no updates
- 🔴 **Commands**: Execute directly, block everything
- 🔴 **User experience**: "Is Blender hung?"

### After (Non-blocking):
- ✅ **Main thread**: Responsive, handles UI updates
- ✅ **Background thread**: Polls Redis independently
- ✅ **Viewport**: Updates in real-time
- ✅ **Commands**: Queued via `bpy.app.timers`, execute when ready
- ✅ **User experience**: Smooth, responsive, real-time feedback!

---

## 📚 Technical Details

### bpy.app.timers.register()

From Blender's C implementation (`source/blender/python/intern/bpy_app_timers.cc`):

```c
/* Registers a function to be called after a certain time interval */
PyDoc_STRVAR(bpy_app_timers_register_doc,
".. function:: register(function, first_interval=0.0, persistent=False)\n"
"\n"
"   Add a new function that will be called after the specified interval.\n"
```

**Key parameters**:
- `function`: Callable to execute in main thread
- `first_interval=0.0`: Execute ASAP (next main thread cycle)
- Returns `None`: Timer runs once and stops (not persistent)

### Thread Safety

**Safe**:
- ✅ Background thread polls Redis
- ✅ Background thread queues via `bpy.app.timers`
- ✅ Main thread executes commands

**Unsafe**:
- ❌ Background thread calling `bpy` functions directly
- ❌ Main thread blocked on I/O operations
- ❌ Long-running operations in main thread

---

## 🔄 Message Flow

```
┌─────────────────┐
│  Redis Stream   │
└────────┬────────┘
         │
         │ xreadgroup() - polls every 5s
         │
         v
┌─────────────────┐
│ Background      │  Daemon thread
│ Consumer Thread │  (doesn't block Blender)
└────────┬────────┘
         │
         │ bpy.app.timers.register()
         │
         v
┌─────────────────┐
│  Timer Queue    │  Blender's internal queue
└────────┬────────┘
         │
         │ Executes when main thread ready
         │
         v
┌─────────────────┐
│ Main Thread     │  Blender's main thread
│ (bpy context)   │  ✨ Viewport updates here!
└────────┬────────┘
         │
         │ router.route(cmd, params)
         │
         v
┌─────────────────┐
│ Command Handler │  create_cube, etc.
│ (bpy operations)│
└─────────────────┘
```

---

## 🛠️ Implementation Checklist

For any Blender Python service that needs to stay responsive:

- [ ] **Use background thread** for I/O operations (Redis, HTTP, etc.)
- [ ] **Make thread daemon** so it won't block Blender exit
- [ ] **Queue commands** via `bpy.app.timers.register(fn, first_interval=0.0)`
- [ ] **Return None** from timer callback (single execution)
- [ ] **Keep main thread responsive** with short sleep intervals
- [ ] **Never** call `bpy` functions directly from background thread

---

## 📖 References

1. **Blender Documentation**: `doc/python_api/rst/info_gotchas_threading.rst`
   - "Python threads cause Blender to crash in hard to diagnose ways"

2. **Blender Source**: `source/blender/python/intern/bpy_app_timers.cc`
   - C implementation of `bpy.app.timers`

3. **blender-mcp**: https://github.com/ahujasid/blender-mcp
   - Socket-based addon that uses this pattern successfully

4. **Our Implementation**: `sidecar/consumer.py`
   - Redis Streams consumer with background thread + timers

---

## 🎓 Lessons Learned

### What blender-mcp Does Better

1. ✅ **Background server thread** - Doesn't block main thread
2. ✅ **`bpy.app.timers` for execution** - Proper main thread queueing
3. ✅ **Daemon threads** - Clean shutdown handling
4. ✅ **Per-command execution** - Each command queued independently

### What We Do Better (First-Class Integration)

1. ✨ **No addon needed** - Built into Blender's source
2. ✨ **Redis Streams** - Better than TCP sockets for distributed systems
3. ✨ **Proper error handling** - SidecarError hierarchy
4. ✨ **Telemetry & metrics** - Built-in tracing and performance monitoring
5. ✨ **Type safety** - Fully typed Python code
6. ✨ **Extensible router** - Clean command handler pattern

---

## 💡 Pro Tips

1. **Short sleep intervals**: Use `time.sleep(0.1)` in main thread wait loop
   - Keeps Blender responsive
   - Allows UI events to process
   - 10 FPS is plenty for background polling

2. **Daemon threads**: Always set `daemon=True`
   - Prevents blocking Blender exit
   - Automatically cleaned up on shutdown

3. **Error handling**: Wrap timer callbacks in try/except
   - Prevents crashes from propagating
   - Logs errors without breaking the queue

4. **Return None**: Timer callbacks must return `None`
   - Prevents timer from repeating
   - Use persistent timers sparingly

5. **Test responsiveness**: Move viewport while command executes
   - If viewport freezes, something's blocking main thread
   - If viewport stays smooth, threading is working!

---

## 🔥 Bottom Line

**If your Blender Python code blocks the main thread, the viewport will freeze.**

Use background threads + `bpy.app.timers` for any I/O operations (network, file, database).

This is THE pattern for real-time, responsive Blender automation.

