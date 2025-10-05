# Quick Start - Degenerate Labs Blender

**Your custom Blender with MCP built in!**

---

## 🚀 Start Blender

```bash
cd /Users/highlander/gamedev/blender

# GUI Mode (see what you're doing)
open ../build_darwin/bin/Blender.app

# Headless Mode (for automation)
../build_darwin/bin/Blender.app/Contents/MacOS/Blender -b
```

**MCP server auto-starts in 2 seconds!**

---

## 🧪 Test MCP Server

```bash
# Simple connection test
python3 test_mcp_socket.py

# Full command test (creates cube in Blender!)
node test_mcp_direct.mjs
```

**Expected output**:
```
✅ Connected to Blender MCP server at localhost:9876
✅ Ping successful
✅ Scene info retrieved
✅ Cube created in Blender!
```

---

## 📡 Send MCP Commands

### Node.js
```javascript
import { createConnection } from 'net';

const client = createConnection({ host: 'localhost', port: 9876 });

// Send command
client.write(JSON.stringify({
  type: 'create_cube',
  params: { location: [5, 5, 0], size: 2 }
}));

// Receive response
client.on('data', (data) => {
  const response = JSON.parse(data.toString());
  console.log(response);
  // { status: "success", result: { name: "Cube.001", ... } }
});
```

### Python
```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9876))

# Send command
command = {
    "type": "get_scene_info",
    "params": {}
}
sock.sendall(json.dumps(command).encode())

# Get response
response = json.loads(sock.recv(8192).decode())
print(response)
# {'status': 'success', 'result': {'objects': 3, ...}}
```

---

## 🎨 Available Commands

### Health Check
```json
{"type": "ping", "params": {}}
```
Returns: `{"status": "success", "result": {"pong": true, "blender_version": "5.0.0 Alpha"}}`

### Scene Info
```json
{"type": "get_scene_info", "params": {}}
```
Returns: `{"status": "success", "result": {"objects": 3, "meshes": 1, "lights": 1, "cameras": 1}}`

### Create Cube
```json
{"type": "create_cube", "params": {"location": [0, 0, 2], "size": 1}}
```
Returns: `{"status": "success", "result": {"name": "Cube.001", "location": [0, 0, 2]}}`

---

## 🔨 Rebuild After Changes

```bash
# Quick rebuild (3-4 seconds!)
make developer ninja

# Check what changed
git status

# Commit
git add <files>
git commit -m "Your changes"

# Push to your fork
git push degen master-degen --no-verify
```

---

## 📚 Documentation

**Start here**:
1. `STATUS.md` - Current state
2. `WHAT_WE_BUILT.md` - What we accomplished
3. `LESSONS_LEARNED.md` - Technical learnings

**Build & setup**:
4. `BUILD_GUIDE.md` - How to build Blender
5. `GIT_WORKFLOW.md` - Git fork workflow

**Architecture**:
6. `MCP_INTEGRATION.md` - MCP server details
7. `docs/sidecar/THREADING.md` - Threading explained

**Future**:
8. `REDIS_BRIDGE_PLAN.md` - Next phase plan

---

## 🎯 Next Steps

1. **Read** `REDIS_BRIDGE_PLAN.md`
2. **Clean up** sidecar code (remove dungeon stuff)
3. **Add more commands** to MCP server
4. **Build Redis bridge** with feature parity
5. **Create separate control project**

---

## 💡 Pro Tips

1. **Keep Blender open** while developing
   - Rebuild in 3-4 seconds
   - Test immediately

2. **Watch the console** when running from terminal
   - See MCP server logs
   - Debug issues quickly

3. **Test with simple scripts first**
   - `test_mcp_socket.py` - Basic connection
   - `test_mcp_direct.mjs` - Full commands
   - Build from there

4. **Commit often**
   - Fast rebuilds mean you can experiment
   - Git makes it easy to revert

---

**You're ready to build!** 🚀

See `REDIS_BRIDGE_PLAN.md` for the roadmap.

