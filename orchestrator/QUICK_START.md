# 🚀 Quick Start: Dungeon Generation

Get up and running in 5 minutes!

---

## Prerequisites

- ✅ Redis running
- ✅ Blender with sidecar
- ✅ Node.js installed

---

## Step 1: Install Dependencies

```bash
cd orchestrator
npm install
```

---

## Step 2: Start Redis

```bash
# Option A: Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option B: Local Redis
redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

---

## Step 3: Start Blender with Sidecar

```bash
# From orchestrator directory
cd ..

# Option A: GUI (recommended for first time)
open ../build_darwin/bin/Blender.app

# Option B: Headless
../build_darwin/bin/Blender.app/Contents/MacOS/Blender --python sidecar.py
```

**Look for these in Blender console:**
```
✅ Consumer thread started
✅ Connected to Redis: localhost:6379
```

---

## Step 4: Test Connection

```bash
cd orchestrator
npm test
```

**Expected output:**
```
[BlenderClient] Sending command: Ping (trace=...)
[BlenderClient] Command succeeded: Ping (trace=...)
✅ Response received:
  Blender Version: 5.0.0 Alpha
  Sidecar Version: 2.0.0-realtime
  ...
```

---

## Step 5: Generate Your First Dungeon! 🏰

```bash
npm run generate
```

**This will:**
1. ✅ Verify Blender connection
2. 🔨 Generate a dungeon (7 rooms, medieval style)
3. 📊 Display statistics
4. 🔥 Animate flickering torches
5. ✨ Complete in ~500ms!

**Then:**
- Switch to Blender window
- Press **SPACEBAR** to play animation
- Use mouse to explore your dungeon!

---

## 🎨 Customize Your Dungeon

Edit `src/examples/test-dungeon-generation.js`:

```javascript
const dungeonConfig = {
  size: 20,           // Larger dungeon!
  rooms: 12,          // More rooms!
  style: 'fantasy',   // Fantasy theme!
  add_lights: true,
  add_player: true,
};
```

**Available styles:**
- `'medieval'` - Stone walls, torches, brown/gray
- `'sci-fi'` - Metal panels, tech lights, blue
- `'fantasy'` - Mystical purple, magical lights

---

## 🧪 Other Test Scripts

```bash
# Test single cube creation
npm run test:cube

# Run the full workflow
npm run generate
```

---

## 🐛 Troubleshooting

### "Connection refused" or "Timeout"

**Problem**: Can't connect to Redis or Blender

**Solution**:
1. Check Redis: `redis-cli ping`
2. Check Blender console for sidecar logs
3. Restart Blender if needed

### "Module not found"

**Problem**: Dependencies not installed

**Solution**: `npm install`

### "Command failed"

**Problem**: Blender sidecar error

**Solution**: Check Blender console for error messages

---

## 📚 Learn More

- **DUNGEON_GENERATION_LEARNING.md** - Complete learning guide
- **REDIS_BRIDGE_DATA_OBJECTS.md** - API reference
- **orchestrator/README.md** - Project overview

---

## 🎯 Next Steps

1. ✨ Experiment with different dungeon configs
2. 🎨 Try different styles (medieval, sci-fi, fantasy)
3. 📈 Increase room count and see performance
4. 🔧 Add your own custom commands
5. 🎮 Export to game engine (coming soon!)

---

**Happy dungeon building!** 🏰🔥

**Degenerate Labs** - Making Blender do degen things!

