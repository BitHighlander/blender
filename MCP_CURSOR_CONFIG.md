# Cursor MCP Configuration for Blender

## Add to Cursor Settings

Open Cursor Settings (Cmd+,) → Search for "MCP" → Edit `mcp_settings.json`

Add this configuration:

```json
{
  "mcpServers": {
    "blender": {
      "command": "node",
      "args": [
        "/Users/highlander/gamedev/blender/mcp_server_stdio.js"
      ],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Alternative: Direct Socket Config (if supported)

If Cursor supports direct socket connections:

```json
{
  "mcpServers": {
    "blender": {
      "type": "socket",
      "host": "localhost",
      "port": 9876
    }
  }
}
```

## Server Details

- **Host**: `localhost`
- **Port**: `9876`
- **Protocol**: JSON over TCP socket
- **Auto-start**: Yes (starts with Blender via `bl_mcp_server.py`)

## Available Commands

- `ping` - Health check
- `get_scene_info` - Get scene statistics  
- `create_cube` - Create a cube mesh

## Testing

1. Start Blender (MCP server auto-starts)
2. Reload Cursor
3. Open Cursor chat and type: "Use MCP to create a cube in Blender at position [5,5,0]"
4. Check Blender - cube should appear!

## Troubleshooting

**Cursor can't connect:**
- Check Blender is running
- Check MCP server started (look for "Blender MCP Server started" in Blender console)
- Try: `telnet localhost 9876` to verify port is open

