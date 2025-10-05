# 🏰 Dungeon Builder Test

Test the real-time, non-blocking sidecar with procedural dungeon generation!

## Prerequisites

1. **Redis running**:
   ```bash
   redis-server
   ```

2. **Node.js with redis package**:
   ```bash
   npm install redis
   ```

3. **Blender sidecar running**:
   ```bash
   ../build_darwin/bin/Blender.app/Contents/MacOS/Blender -b --python sidecar.py
   ```

## Running the Test

```bash
# Make sure Redis is running
redis-cli ping  # Should return PONG

# Run the dungeon builder test
node test_dungeon.mjs
```

## What It Does

The test script will:

1. ✅ **Verify sidecar version** (`2.0.0-realtime`)
2. 🏰 **Build a procedural dungeon** with:
   - 7 rooms with stone walls
   - Connecting corridors
   - Flickering torch lights  
   - Medieval decorations (pillars)
   - Player spawn point
   - Camera setup
3. 📊 **Get dungeon statistics**
4. 🔥 **Animate flickering torches**

## Expected Output

```
🚀 Degenerate Labs Blender - Dungeon Builder Test

Connecting to Redis...
✅ Connected to Redis

════════════════════════════════════════════════════════════
STEP 1: Verify Sidecar Version
════════════════════════════════════════════════════════════

📤 Sending: Ping { echo: 'version check' }
✅ Success (45ms): {
  echo: 'version check',
  sidecar_version: '2.0.0-realtime',
  worker_id: 'worker-001',
  hostname: 'your-mac',
  blender_version: '5.0.0',
  blender_build: 'darwin-arm64'
}

📊 Sidecar Info:
   Version: 2.0.0-realtime ✨
   Worker:  worker-001
   Blender: 5.0.0
   Build:   darwin-arm64

✅ Correct version: 2.0.0-realtime (with bpy.app.timers!)

════════════════════════════════════════════════════════════
STEP 2: BUILD THE DUNGEON! 🏰
════════════════════════════════════════════════════════════

🔨 Building dungeon with parameters:
{
  "size": 12,
  "rooms": 7,
  "style": "medieval",
  "add_lights": true,
  "add_player": true
}

📤 Sending: CreateDungeon { size: 12, rooms: 7, ... }
✅ Success (342ms): {...}

🏰 Dungeon 'Dungeon_medieval_1696531234' created with 7 rooms and 47 objects in 0.34s!
   Dungeon Name: Dungeon_medieval_1696531234
   Rooms: 7
   Objects: 47
   Build Time: 0.34s

════════════════════════════════════════════════════════════
STEP 3: Dungeon Statistics
════════════════════════════════════════════════════════════

📤 Sending: GetDungeonStats {}
✅ Success (12ms): {...}

📊 Dungeon stats: 7 rooms, 28 walls, 28 lights
   Stats: { total_objects: 47, rooms: 7, walls: 28, lights: 28, ... }

════════════════════════════════════════════════════════════
STEP 4: Animate Flickering Torches 🔥
════════════════════════════════════════════════════════════

📤 Sending: AnimateDungeon { intensity: 0.3, speed: 1.0, duration: 120 }
✅ Success (156ms): {...}

🔥 Animated 28 torches with flickering!
   Lights animated: Torch_1_2_0, Torch_1_2_1, ...
   Duration: 120 frames

════════════════════════════════════════════════════════════
✨ SUCCESS! Dungeon Built and Animated!
════════════════════════════════════════════════════════════

💡 The viewport should be updating in REAL-TIME!
   This proves bpy.app.timers is working correctly.

🎮 Open Blender and explore your dungeon!
   Run: open ../build_darwin/bin/Blender.app
```

## What This Tests

### Real-Time Threading ✨

The dungeon is built with **multiple commands** sent in sequence. Each command:

1. **Received by background thread** (Redis consumer)
2. **Queued via `bpy.app.timers`** (non-blocking)
3. **Executed in main thread** (viewport updates!)
4. **Response sent immediately**

**Key Feature**: Blender's viewport stays **responsive** throughout!

You can:
- ✅ Rotate the viewport while dungeon builds
- ✅ See objects appear in real-time
- ✅ Play the animation immediately
- ✅ No freezing or hanging!

### Commands Tested

1. **`Ping`** - Version verification
2. **`CreateDungeon`** - Procedural generation (creates ~50 objects)
3. **`GetDungeonStats`** - Scene introspection
4. **`AnimateDungeon`** - Keyframe animation

## Dungeon Styles

Change the `style` parameter:

- **`medieval`** - Stone walls, torches, pillars (brown/gray)
- **`sci-fi`** - Metal walls, tech panels, blue lighting
- **`fantasy`** - Mystical purple walls, crystals, magical lights

## Customization

Edit `test_dungeon.mjs` to change:

```javascript
const dungeonParams = {
  size: 15,           // Larger dungeon
  rooms: 10,          // More rooms
  style: 'fantasy',   // Fantasy theme
  add_lights: true,
  add_player: true,
};
```

## Troubleshooting

### "Connection refused"
- Make sure Redis is running: `redis-server`

### "Timeout waiting for response"
- Check sidecar is running: Look for "✅ Consumer thread started"
- Check Redis connection in sidecar logs

### "Module not found"
- Install redis: `npm install redis`

## Files Created

- **`test_dungeon.mjs`** - Node.js orchestrator script
- **`sidecar/commands/dungeon.py`** - Dungeon builder implementation
- **`sidecar/__init__.py`** - Version bumped to 2.0.0-realtime

## Next Steps

After successful test:

1. ✨ Open Blender and see your dungeon!
2. 🎬 Press spacebar to play torch animation
3. 🔧 Modify the dungeon code and rebuild
4. 🎨 Add more decorations, enemies, loot!
5. 🚀 Build your own game procedural gen tools!

---

**Degenerate Labs** - Making Blender do degen things! 🔥

