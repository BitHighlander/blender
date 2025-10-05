# Milestone 1: Real-Time Dungeon Mesh Generation

**Branch:** `feature/realtime-dungeon-mesh`  
**Goal:** Create a simple dungeon mesh that you can see being built in real-time in Blender's viewport

---

## Objective

Send commands from outside Blender (via Redis) that create visible geometry that appears immediately in the Blender window you're watching.

**Success Criteria:**
- Command triggers mesh creation
- Mesh appears instantly in viewport
- Can see geometry being built step-by-step
- Simple dungeon layout (rooms + corridors)

---

## Phase 1: CreateCube Command

**Goal:** Prove we can create visible geometry

### Tasks
- [ ] Implement `CreateCube` command handler
- [ ] Parameters: position (x, y, z), size
- [ ] Test: Send command, cube appears in viewport
- [ ] Verify you can SEE it in your open Blender window

### Command Spec
```python
{
  "cmd": "CreateCube",
  "params": {
    "name": "TestCube",
    "location": [0, 0, 0],
    "size": 2.0
  }
}
```

---

## Phase 2: CreateRoom Command

**Goal:** Create a simple rectangular room

### Tasks
- [ ] Implement `CreateRoom` command
- [ ] Parameters: width, depth, height, position
- [ ] Create floor, walls, ceiling as separate objects
- [ ] Test: Send command, room appears

### Command Spec
```python
{
  "cmd": "CreateRoom",
  "params": {
    "name": "Room_01",
    "location": [0, 0, 0],
    "width": 10.0,
    "depth": 10.0,
    "height": 3.0
  }
}
```

---

## Phase 3: CreateCorridor Command

**Goal:** Connect rooms with corridors

### Tasks
- [ ] Implement `CreateCorridor` command
- [ ] Parameters: start, end, width, height
- [ ] Create corridor mesh between two points
- [ ] Test: Create two rooms, add corridor between them

### Command Spec
```python
{
  "cmd": "CreateCorridor",
  "params": {
    "name": "Corridor_01",
    "start": [0, 0, 0],
    "end": [10, 0, 0],
    "width": 2.0,
    "height": 3.0
  }
}
```

---

## Phase 4: BuildDungeon Command

**Goal:** Build a complete simple dungeon

### Tasks
- [ ] Implement `BuildDungeon` command
- [ ] Takes a simple dungeon spec (JSON)
- [ ] Creates all rooms and corridors
- [ ] Test: Send spec, watch dungeon appear

### Dungeon Spec Example
```python
{
  "cmd": "BuildDungeon",
  "params": {
    "name": "TestDungeon_01",
    "rooms": [
      {
        "id": "room_1",
        "location": [0, 0, 0],
        "width": 10,
        "depth": 10,
        "height": 3
      },
      {
        "id": "room_2",
        "location": [15, 0, 0],
        "width": 8,
        "depth": 8,
        "height": 3
      }
    ],
    "corridors": [
      {
        "from": "room_1",
        "to": "room_2",
        "width": 2,
        "height": 3
      }
    ]
  }
}
```

---

## Phase 5: Real-Time Progress

**Goal:** See dungeon being built step-by-step

### Tasks
- [ ] Add delays between operations
- [ ] Emit progress events
- [ ] Watch each room appear one at a time
- [ ] Watch corridors connect them

---

## Testing Plan

### Manual Tests

1. **Single Cube Test**
   ```bash
   redis-cli XADD blender:cmd "*" payload '{
     "cmd": "CreateCube",
     "params": {"name": "TestCube", "location": [0, 0, 0], "size": 2}
   }'
   ```
   - Expected: Cube appears at origin

2. **Single Room Test**
   ```bash
   redis-cli XADD blender:cmd "*" payload '{
     "cmd": "CreateRoom",
     "params": {
       "name": "TestRoom",
       "location": [0, 0, 0],
       "width": 10,
       "depth": 10,
       "height": 3
     }
   }'
   ```
   - Expected: Room box appears

3. **Two Rooms + Corridor**
   - Create room 1 at [0, 0, 0]
   - Create room 2 at [15, 0, 0]
   - Create corridor connecting them
   - Expected: Complete connected dungeon

4. **Full Dungeon Build**
   - Send BuildDungeon command
   - Expected: Entire dungeon appears progressively

---

## Implementation Notes

### Blender API to Use

```python
import bpy

# Create mesh
mesh = bpy.data.meshes.new("MeshName")
obj = bpy.data.objects.new("ObjectName", mesh)
bpy.context.collection.objects.link(obj)

# Create cube from primitives
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), size=2)

# Force viewport update
bpy.context.view_layer.update()
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
```

### Viewport Update Strategy

To see geometry appear in real-time:
1. Create geometry
2. Call `bpy.context.view_layer.update()`
3. Force viewport redraw
4. Optional: Add small delay for visual effect

---

## Deliverables

1. **New Commands**
   - `sidecar/commands/mesh.py` - CreateCube
   - `sidecar/commands/dungeon.py` - CreateRoom, CreateCorridor, BuildDungeon

2. **Tests**
   - `tests/test_create_cube.py`
   - `tests/test_create_room.py`
   - `tests/test_build_dungeon.py`

3. **Documentation**
   - Update SPEC.md with new commands
   - Add examples to QUICKSTART.md

---

## Success Demo

```bash
# Terminal 1: Blender is open with sidecar running

# Terminal 2: Build a simple dungeon
python tests/test_build_dungeon.py

# Watch in Blender window as:
# 1. First room appears
# 2. Second room appears
# 3. Corridor connects them
# 4. Complete dungeon visible!
```

---

## Time Estimate

- Phase 1 (CreateCube): 1-2 hours
- Phase 2 (CreateRoom): 2-3 hours
- Phase 3 (CreateCorridor): 2-3 hours
- Phase 4 (BuildDungeon): 2-3 hours
- Phase 5 (Real-time effects): 1 hour
- Testing & Polish: 2 hours

**Total: ~10-14 hours** (1-2 days)

---

## Next Steps

1. Start with CreateCube command
2. Test it works and is visible
3. Build up to rooms and corridors
4. Create full dungeon builder

Let's build something you can SEE! 🏰

