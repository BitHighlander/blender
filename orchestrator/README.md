# Dungeon Orchestrator

> High-level orchestrator for procedural dungeon generation via Blender Redis Sidecar

This Node.js project handles the **game logic** and **dungeon generation algorithms**, keeping the Blender sidecar clean and minimal.

---

## Architecture

```
┌────────────────────┐         ┌─────────┐         ┌──────────────┐
│   Orchestrator     │ XADD    │  Redis  │ XREAD   │   Blender    │
│    (Node.js)       ├────────>│ Streams │<────────┤   Sidecar    │
│                    │         │         │         │   (Python)   │
│  - Dungeon Logic   │<────────┤         ├────────>│ - Primitives │
│  - Room Layout     │  XREAD  │         │  XADD   │ - Mesh Ops   │
│  - Pathfinding     │         │         │         │ - Export     │
└────────────────────┘         └─────────┘         └──────────────┘
```

### Division of Responsibilities

**Orchestrator (This Project):**
- Dungeon generation algorithms
- Room placement logic
- Corridor routing
- Game rules & constraints
- High-level commands (BuildDungeon, etc.)

**Blender Sidecar:**
- Low-level Blender API primitives only
- Create meshes (cubes, planes, etc.)
- Transform objects
- Export to files
- NO game logic

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Redis (if not running)

```bash
# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or local Redis
redis-server
```

### 3. Start Blender with Sidecar

```bash
# From orchestrator directory
cd ..
open ../build_darwin/bin/Blender.app
# Sidecar auto-starts with Redis bridge!
```

Or run Blender with sidecar manually:
```bash
cd ..
../build_darwin/bin/Blender.app/Contents/MacOS/Blender --python sidecar.py
```

### 4. Test Connection

```bash
npm test
```

Expected output:
```
✅ Response received:
  Blender Version: 5.0.0 Alpha
  Sidecar Version: 1.0.0-dev
  Worker ID: your-hostname
  Echo: Hello from Node.js orchestrator!

✅ SUCCESS: Orchestrator ↔ Blender communication working!
```

---

## Project Structure

```
dungeon-orchestrator/
├── src/
│   ├── lib/
│   │   └── blender-client.js    # Redis client for Blender
│   ├── commands/
│   │   └── (high-level commands)
│   ├── dungeon/
│   │   ├── generator.js         # Dungeon generation algorithm
│   │   ├── room-placer.js       # Room placement logic
│   │   └── corridor-router.js   # Corridor pathfinding
│   ├── examples/
│   │   ├── test-ping.js         # Test connection
│   │   ├── test-cube.js         # Create a single cube
│   │   ├── test-room.js         # Create a room
│   │   └── test-dungeon.js      # Build full dungeon
│   └── index.js                 # Main entry point
├── package.json
└── README.md
```

---

## Usage Examples

### Ping Blender

```javascript
import { BlenderClient } from './src/lib/blender-client.js';

const client = new BlenderClient();

const response = await client.ping('Hello!');
console.log('Blender version:', response.result.blender_version);

await client.close();
```

### Create a Cube

```javascript
const response = await client.createCube({
  name: 'TestCube',
  location: [0, 0, 0],
  size: 2.0
});
```

### Create a Room

```javascript
const response = await client.createRoom({
  name: 'StartRoom',
  location: [0, 0, 0],
  width: 10,
  depth: 10,
  height: 3
});
```

### Build a Dungeon (Future)

```javascript
import { DungeonGenerator } from './src/dungeon/generator.js';

const generator = new DungeonGenerator(client);

const dungeon = await generator.generate({
  roomCount: 5,
  minRoomSize: 8,
  maxRoomSize: 15,
  corridorWidth: 2
});
```

---

## Development

### Run Examples

```bash
# Test connection
npm test

# Test cube creation
npm run test:cube

# Test room creation
npm run test:room

# Test full dungeon
npm run test:dungeon
```

### Add New Commands

1. Add method to `BlenderClient` in `src/lib/blender-client.js`
2. Implement handler in Blender sidecar (`sidecar/commands/`)
3. Create test in `src/examples/`

---

## Environment Variables

Create a `.env` file:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
COMMAND_STREAM=blender:cmd
REPLY_STREAM=blender:reply
TIMEOUT=10000
```

---

## Next Steps

- [x] Basic client & ping test
- [ ] CreateCube command
- [ ] CreateRoom command
- [ ] CreateCorridor command
- [ ] DungeonGenerator algorithm
- [ ] Room placement logic
- [ ] Corridor routing
- [ ] Real-time visualization
- [ ] Export to .glb files

---

## Philosophy

This orchestrator is the **brain**, Blender is the **hands**.

- **Orchestrator knows:** "I need a 10x10 room at position (5, 0, 0)"
- **Blender knows:** "Here's how to create a mesh representing that room"

Keep Blender commands **simple and reusable**. All complexity lives here.

---

## Contributing

See main project README for development guidelines.

