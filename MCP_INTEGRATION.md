# Blender MCP Integration - Degenerate Labs

## Goal
Run **blender-mcp** (proven, solid MCP server) in our custom Blender build.

## Architecture

```
┌──────────────┐         MCP Protocol        ┌─────────────────┐
│ Cursor Agent │ ◄─────────────────────────► │  FastMCP Server │
│  (or Node.js)│                              │  (main.py)      │
└──────────────┘                              └────────┬────────┘
                                                       │
                                              Socket (localhost:9876)
                                                       │
                                              ┌────────▼────────┐
                                              │ Blender Addon   │
                                              │ (addon.py)      │
                                              │  - Socket server│
                                              │  - bpy.app.timers│
                                              └────────┬────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │  Blender Core   │
                                              │  (your build)   │
                                              └─────────────────┘
```

## Components

### 1. Blender Addon (`scripts/addons/blender_mcp`)
- **Source**: blender-mcp by ahujasid
- **Location**: Auto-installed in our Blender build
- **Function**: Runs socket server on port 9876
- **Threading**: Uses `bpy.app.timers.register()` (proven safe!)
- **Auto-start**: `scripts/startup/blender_mcp_autostart.py`

### 2. FastMCP Server (`mcp_server/`)
- **Source**: blender-mcp server.py
- **Function**: Connects to Blender addon socket
- **Protocol**: MCP (Model Context Protocol)
- **Port**: localhost:9876 (Blender addon socket)

## Setup

### 1. Start Blender with MCP Addon
```bash
# GUI mode (see what's happening)
open ../build_darwin/bin/Blender.app

# Or headless mode
../build_darwin/bin/Blender.app/Contents/MacOS/Blender
```

**The addon auto-starts!** You'll see in console:
```
✅ Blender MCP addon enabled
🚀 Blender MCP addon loaded and ready
   Socket server on localhost:9876
```

### 2. Start FastMCP Server
```bash
cd mcp_server
uv run main.py
```

### 3. Test MCP Connection
```bash
# From Cursor or your MCP client
# The server exposes tools like:
# - create_cube
# - create_sphere  
# - execute_python
# - get_scene_info
# etc.
```

## Testing

### Node.js MCP Test (Simple)
```javascript
// test_mcp.mjs
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "uv",
  args: ["run", "mcp_server/main.py"]
});

const client = new Client({
  name: "blender-test-client",
  version: "1.0.0"
}, {
  capabilities: {}
});

await client.connect(transport);

// List available tools
const tools = await client.listTools();
console.log("Available Blender tools:", tools);

// Call a tool
const result = await client.callTool({
  name: "create_cube",
  arguments: { location: [0, 0, 0], size: 2 }
});
console.log("Result:", result);
```

## Why This Approach?

### ✅ Proven
- blender-mcp is battle-tested
- Socket + bpy.app.timers pattern works
- Thousands of users

### ✅ Flexible
- MCP protocol is standard
- Any MCP client can connect
- Cursor agent native support

### ✅ First-Class
- Built into YOUR Blender
- Auto-starts on launch
- No external dependencies

### ✅ Real-Time
- Non-blocking execution
- Viewport stays responsive
- bpy.app.timers queuing

## vs Redis Sidecar?

**Keep both!** They serve different purposes:

| Feature | MCP (blender-mcp) | Redis Sidecar |
|---------|-------------------|---------------|
| **Protocol** | MCP (standard) | Redis Streams |
| **Clients** | Cursor, Claude Desktop | Distributed workers |
| **Use Case** | Interactive AI agents | Backend automation |
| **Deployment** | Single machine | Multi-worker scale |

## Next Steps

1. ✅ Addon installed and auto-starting
2. ⏳ Set up FastMCP server
3. ⏳ Test with Cursor agent
4. ⏳ Create simple test commands
5. ⏳ Document MCP tools available

---

**Focus: Get MCP working, not build dungeons!** 🎯

