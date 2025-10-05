# MMO Dungeon Generation Game Plan

**Project:** Large-Scale Procedural Dungeon Generation for MMO  
**Architecture:** Blender Sidecar + Orchestrator Pipeline  
**Target:** Production-ready dungeon streaming system  
**Date:** October 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scale & Requirements](#scale--requirements)
3. [Architecture Overview](#architecture-overview)
4. [Generation Pipeline](#generation-pipeline)
5. [Asset Strategy](#asset-strategy)
6. [Spatial Partitioning](#spatial-partitioning)
7. [Implementation Phases](#implementation-phases)
8. [Performance Targets](#performance-targets)
9. [Tech Stack](#tech-stack)
10. [Example Workflows](#example-workflows)

---

## Executive Summary

### The Vision

Generate massive, procedurally-created dungeons that:
- **Scale to MMO requirements** (100+ concurrent players per instance)
- **Stream seamlessly** (chunks load/unload based on player position)
- **Feel handcrafted** (high visual quality, not "random")
- **Generate fast** (< 10s for entire dungeon, instant for single chunk)
- **Support gameplay** (collision, navmesh, zones, spawners)

### Core Approach

```
┌──────────────┐
│ Orchestrator │  High-level logic (graph, layout, rules)
└──────┬───────┘
       │ Redis Commands
       ↓
┌──────────────┐
│ Blender      │  Geometry realization (instancing, export)
│ Sidecar      │  Asset composition, lighting, materials
└──────┬───────┘
       │ GLB files
       ↓
┌──────────────┐
│ Game Engine  │  Runtime streaming, collision, gameplay
│ (Unity/UE)   │
└──────────────┘
```

**Key Principle:** Orchestrator handles **procedural logic**, Blender handles **geometry realization**.

---

## Scale & Requirements

### Target Specifications

| Metric | Target | Notes |
|--------|--------|-------|
| **Dungeon Size** | 1km × 1km | Large MMO instance |
| **Room Count** | 500-2000 rooms | Varies by dungeon type |
| **Chunk Size** | 50m × 50m | Streaming unit (20×20 chunks) |
| **Assets** | 200-500 unique | Modular kit pieces |
| **Generation Time** | < 10 seconds | Full dungeon |
| **Chunk Load Time** | < 100ms | Single chunk from cache |
| **Players/Instance** | 100+ | Concurrent players |
| **Memory Budget** | 4GB | Total dungeon data |

### Gameplay Requirements

**Must Support:**
- ✅ Player navigation (collision meshes)
- ✅ AI pathfinding (navmesh)
- ✅ Monster spawners (metadata)
- ✅ Treasure/loot placement
- ✅ Boss arenas (special rooms)
- ✅ Teleport points
- ✅ Environmental hazards (traps, lava)
- ✅ Dynamic events (doors, switches)

---

## Architecture Overview

### Component Roles

#### 1. **Orchestrator (Python/Node.js)**
**Responsibility:** Procedural generation logic

- Graph generation (WFC, BSP, cellular automata)
- Room placement and connectivity
- Theme selection and variation
- Metadata generation (spawners, zones)
- Chunk boundaries and LODs
- Caching and versioning

#### 2. **Blender Sidecar (Python + bpy)**
**Responsibility:** Geometry realization

- Asset instancing (rooms, props, decorations)
- Collection management
- Geometry Nodes evaluation (procedural details)
- Material assignment
- Lighting baking (optional)
- GLB/GLTF export per chunk

#### 3. **Redis (Message Broker)**
**Responsibility:** Command transport

- Command queue (`blender:cmd`)
- Response stream (`blender:reply`)
- Event stream (`blender:events`)
- Worker health (`blender:health`)

#### 4. **Asset Library (.blend files)**
**Responsibility:** Modular kit pieces

- Room templates (10m×10m, 20m×20m, etc.)
- Corridors (straight, L-turn, T-junction)
- Props (doors, pillars, torches, crates)
- Decorations (vines, rubble, water)
- Special rooms (boss arena, treasure vault)

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                         │
│                                                         │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ Graph Gen    │─>│ Room Place │─>│ Chunk Split   │  │
│  │ (Algorithm)  │  │ (Layout)   │  │ (Streaming)   │  │
│  └──────────────┘  └────────────┘  └───────┬───────┘  │
│                                             │          │
└─────────────────────────────────────────────┼──────────┘
                                              │
                                              │ Redis Command
                                              ↓
┌─────────────────────────────────────────────────────────┐
│                   BLENDER SIDECAR                       │
│                                                         │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ Load Assets  │─>│ Instance   │─>│ Export GLB    │  │
│  │ (.blend)     │  │ (Transform)│  │ (Per Chunk)   │  │
│  └──────────────┘  └────────────┘  └───────┬───────┘  │
│                                             │          │
└─────────────────────────────────────────────┼──────────┘
                                              │
                                              │ GLB Files
                                              ↓
┌─────────────────────────────────────────────────────────┐
│                    GAME ENGINE                          │
│                                                         │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ Stream Mgr   │─>│ Physics    │─>│ Gameplay      │  │
│  │ (Load/Unload)│  │ (Collision)│  │ (Spawners)    │  │
│  └──────────────┘  └────────────┘  └───────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Generation Pipeline

### Phase 1: High-Level Layout (Orchestrator)

**Algorithm:** Wave Function Collapse (WFC) or Binary Space Partition (BSP)

```python
# Pseudo-code for orchestrator
dungeon = DungeonGenerator(
    seed=12345,
    size=(1000, 1000),  # 1km × 1km
    room_density=0.7,
    algorithm="wfc"
)

# Generate abstract graph
graph = dungeon.generate_graph()
# Nodes: rooms, corridors
# Edges: connections

# Place rooms in world space
layout = dungeon.place_rooms(graph)
# Output: {room_id: {position, rotation, template_id}}

# Add gameplay metadata
metadata = dungeon.add_gameplay_data(layout)
# Output: spawners, loot, zones, events
```

**Output:** JSON manifest
```json
{
  "dungeon_id": "crypt_001",
  "seed": 12345,
  "bounds": {"min": [0, 0], "max": [1000, 1000]},
  "rooms": [
    {
      "id": "room_0",
      "template": "rect_10x10_stone",
      "position": [100, 200, 0],
      "rotation": [0, 0, 45],
      "zone": "entrance",
      "spawners": [
        {"type": "skeleton", "count": 3, "position": [5, 5, 0]}
      ]
    },
    // ... 500-2000 rooms
  ],
  "corridors": [
    {
      "id": "corridor_0",
      "template": "straight_5m",
      "connects": ["room_0", "room_1"],
      "position": [105, 205, 0]
    }
  ]
}
```

---

### Phase 2: Chunk Subdivision (Orchestrator)

**Purpose:** Enable streaming by splitting dungeon into chunks

```python
# Divide dungeon into 50m × 50m chunks
chunks = dungeon.subdivide_into_chunks(
    chunk_size=50,
    overlap=2  # 2m overlap for seamless stitching
)

# Each chunk gets:
# - List of rooms/corridors within bounds
# - Border connections (portals to adjacent chunks)
# - Metadata (spawners, loot)

for chunk in chunks:
    chunk_manifest = {
        "chunk_id": f"chunk_{chunk.x}_{chunk.y}",
        "bounds": chunk.bounds,
        "rooms": chunk.rooms,
        "corridors": chunk.corridors,
        "neighbors": chunk.get_neighbors(),
        "lod_levels": [0, 1, 2]  # For distance LODs
    }
    save_chunk_manifest(chunk_manifest)
```

**Output:** 400 chunk manifests (20×20 grid)

---

### Phase 3: Geometry Realization (Blender Sidecar)

**For each chunk, send command to Blender:**

```python
# Orchestrator sends Redis command
send_command({
    "cmd": "GenerateDungeonChunk",
    "params": {
        "chunk_id": "chunk_5_10",
        "manifest": chunk_manifest,
        "asset_library": "/assets/dungeon_crypt.blend",
        "export_path": "/build/dungeons/crypt_001/chunk_5_10.glb",
        "lod_level": 0,
        "options": {
            "bake_lighting": False,
            "collision_mesh": True,
            "navmesh": True
        }
    }
})
```

**Blender Sidecar Processing:**

```python
# sidecar/commands/dungeon.py

def generate_dungeon_chunk(chunk_id, manifest, asset_library, export_path, lod_level, options):
    """
    Generate a single dungeon chunk from manifest
    """
    # 1. Load asset library
    load_blend(asset_library, link=True)
    
    # 2. Create chunk collection
    create_collection(name=chunk_id, parent="Scene")
    
    # 3. Instance rooms
    for room in manifest["rooms"]:
        instance_collection(
            collection=room["template"],
            parent=chunk_id,
            name=room["id"],
            transform={
                "position": room["position"],
                "rotation": room["rotation"]
            }
        )
    
    # 4. Instance corridors
    for corridor in manifest["corridors"]:
        instance_collection(
            collection=corridor["template"],
            parent=chunk_id,
            name=corridor["id"],
            transform={
                "position": corridor["position"],
                "rotation": corridor["rotation"]
            }
        )
    
    # 5. Add decorations (Geometry Nodes)
    if lod_level == 0:  # Only for close-up LOD
        attach_node_group(
            object=chunk_id,
            node_group="NG_Scatter_Props",
            params={"density": 0.5, "seed": manifest["seed"]}
        )
    
    # 6. Generate collision mesh (simplified)
    if options["collision_mesh"]:
        create_collision_mesh(chunk_id)
    
    # 7. Export to GLB
    export_gltf(
        filepath=export_path,
        selection=[chunk_id],
        export_format="GLB"
    )
    
    # 8. Generate navmesh (separate export)
    if options["navmesh"]:
        generate_navmesh(chunk_id, export_path.replace(".glb", "_nav.obj"))
    
    return {
        "chunk_id": chunk_id,
        "export_path": export_path,
        "file_size_mb": get_file_size(export_path) / 1024 / 1024,
        "poly_count": get_poly_count(chunk_id)
    }
```

**Output per chunk:**
- `chunk_5_10.glb` - Main geometry (10-50MB)
- `chunk_5_10_nav.obj` - Navmesh (1-5MB)
- `chunk_5_10_collision.obj` - Simplified collision (optional)
- `chunk_5_10_metadata.json` - Gameplay data

---

### Phase 4: Streaming Runtime (Game Engine)

**Unity/Unreal Implementation:**

```csharp
// ChunkStreamingManager.cs

public class ChunkStreamingManager : MonoBehaviour {
    Dictionary<Vector2Int, ChunkData> loadedChunks = new();
    Vector2Int currentPlayerChunk;
    int loadRadius = 2;  // Load 2 chunks in each direction
    
    void Update() {
        Vector2Int newChunk = WorldPosToChunk(player.position);
        
        if (newChunk != currentPlayerChunk) {
            currentPlayerChunk = newChunk;
            UpdateLoadedChunks();
        }
    }
    
    void UpdateLoadedChunks() {
        // Determine which chunks should be loaded
        HashSet<Vector2Int> desiredChunks = GetChunksInRadius(currentPlayerChunk, loadRadius);
        
        // Unload chunks outside radius
        foreach (var chunk in loadedChunks.Keys.ToList()) {
            if (!desiredChunks.Contains(chunk)) {
                UnloadChunk(chunk);
            }
        }
        
        // Load new chunks
        foreach (var chunk in desiredChunks) {
            if (!loadedChunks.ContainsKey(chunk)) {
                LoadChunkAsync(chunk);
            }
        }
    }
    
    async Task LoadChunkAsync(Vector2Int chunkCoord) {
        string path = $"Dungeons/crypt_001/chunk_{chunkCoord.x}_{chunkCoord.y}.glb";
        
        // Load GLB asynchronously
        GameObject chunkObj = await GLTFLoader.LoadAsync(path);
        
        // Load metadata
        ChunkMetadata metadata = LoadMetadata(chunkCoord);
        
        // Spawn gameplay elements
        SpawnMonsters(metadata.spawners);
        SpawnLoot(metadata.loot);
        
        // Add to physics
        AddColliders(chunkObj);
        
        loadedChunks[chunkCoord] = new ChunkData {
            gameObject = chunkObj,
            metadata = metadata
        };
    }
    
    void UnloadChunk(Vector2Int chunkCoord) {
        if (loadedChunks.TryGetValue(chunkCoord, out ChunkData chunk)) {
            Destroy(chunk.gameObject);
            loadedChunks.Remove(chunkCoord);
        }
    }
}
```

---

## Asset Strategy

### Modular Kit System

**Design Philosophy:** LEGO-like pieces that snap together

#### Asset Categories

**1. Room Templates** (50-100 variants)
```
rooms/
├── rect_10x10_stone/        # Basic stone room
│   ├── floor.mesh
│   ├── walls.mesh
│   ├── ceiling.mesh
│   └── sockets/             # Connection points
│       ├── north_door.empty
│       ├── south_door.empty
│       ├── east_door.empty
│       └── west_door.empty
│
├── rect_20x20_pillared/     # Large pillared hall
├── circle_15_arena/         # Boss arena
├── L_shaped_10x15/          # L-shaped room
└── irregular_cave/          # Organic cave
```

**2. Corridors** (20-30 variants)
```
corridors/
├── straight_5m/
├── straight_10m/
├── L_turn_90deg/
├── T_junction/
├── cross_junction/
└── stairs_up_5m/
```

**3. Props & Decorations** (200-300 assets)
```
props/
├── doors/                   # 10-20 types
├── pillars/                 # 5-10 types
├── lights/                  # Torches, braziers
├── furniture/               # Tables, chairs, crates
├── vegetation/              # Vines, moss, mushrooms
└── debris/                  # Rubble, bones, trash
```

**4. Materials & Textures**
```
materials/
├── stone_wall_01.mat        # PBR material
├── stone_floor_cracked.mat
├── wood_door_old.mat
├── metal_rusty.mat
└── water_murky.mat
```

### Asset Specifications

| Asset Type | Poly Budget | Texture Resolution | LOD Levels |
|------------|-------------|-------------------|------------|
| Room (10×10) | 5k-10k tris | 2048×2048 | 3 |
| Corridor | 2k-5k tris | 1024×1024 | 2 |
| Large Prop | 1k-3k tris | 1024×1024 | 2 |
| Small Prop | 200-500 tris | 512×512 | 1 |
| Decoration | 50-200 tris | 512×512 | 0 (culled) |

---

## Spatial Partitioning

### Chunk System

**Design:** Fixed-size chunks for predictable streaming

```
Chunk Grid (20×20 = 400 chunks)
┌──┬──┬──┬──┬──┬──┬──┬──┐
│  │  │  │  │  │  │  │  │  Each chunk: 50m × 50m
├──┼──┼──┼──┼──┼──┼──┼──┤  Contains: 5-20 rooms
│  │██│██│  │  │  │  │  │  Border overlap: 2m
├──┼██┼██┼──┼──┼──┼──┼──┤
│  │██│██│  │  │  │  │  │  ██ = Currently loaded
├──┼──┼──┼──┼──┼──┼──┼──┤      (player in center)
│  │  │  │  │  │  │  │  │
```

### LOD Strategy

**Level of Detail based on distance:**

| LOD Level | Distance | Poly Reduction | Details |
|-----------|----------|----------------|---------|
| **LOD 0** (Full) | 0-50m | 100% | All props, decorations |
| **LOD 1** (Medium) | 50-100m | 50% | Major props only |
| **LOD 2** (Low) | 100-200m | 25% | Geometry only |
| **LOD 3** (Culled) | 200m+ | 0% | Not rendered |

**Implementation:**
```python
# Generate multiple LODs per chunk
for lod in [0, 1, 2]:
    send_command({
        "cmd": "GenerateDungeonChunk",
        "params": {
            "chunk_id": f"chunk_5_10_lod{lod}",
            "lod_level": lod,
            # ... other params
        }
    })
```

---

## Implementation Phases

### Phase 1: Proof of Concept (1-2 weeks)

**Goal:** Generate single room and corridor

**Tasks:**
- [ ] Create basic room asset (10×10m stone room)
- [ ] Create corridor asset (5m straight)
- [ ] Implement `GenerateDungeonChunk` command
- [ ] Export single chunk to GLB
- [ ] Import GLB in Unity/Unreal
- [ ] Test: Walk through generated geometry

**Success Criteria:**
- Single room + corridor loads in game engine
- Collision works
- Visual quality acceptable

---

### Phase 2: Small Dungeon (2-3 weeks)

**Goal:** Generate 50-room dungeon with graph algorithm

**Tasks:**
- [ ] Implement BSP or WFC algorithm in orchestrator
- [ ] Create 10 room templates (various sizes)
- [ ] Create 5 corridor templates
- [ ] Generate dungeon manifest (50 rooms)
- [ ] Batch-generate all chunks via Blender sidecar
- [ ] Export complete dungeon (50 GLB files)
- [ ] Test: Load all chunks at once (no streaming)

**Success Criteria:**
- 50-room dungeon generates in < 30 seconds
- All rooms connected and navigable
- No visual artifacts (gaps, overlaps)

---

### Phase 3: Streaming System (2-3 weeks)

**Goal:** Implement chunk streaming in game engine

**Tasks:**
- [ ] Subdivide dungeon into chunks (50m grid)
- [ ] Implement chunk streaming manager (Unity/Unreal)
- [ ] Add chunk loading/unloading
- [ ] Add LOD switching
- [ ] Test with 100+ rooms (400 chunks)
- [ ] Profile memory and performance

**Success Criteria:**
- Chunks load < 100ms each
- Memory stays under 4GB
- 60 FPS maintained
- Smooth streaming (no hitches)

---

### Phase 4: Asset Library (3-4 weeks)

**Goal:** Create production-quality asset library

**Tasks:**
- [ ] Model 50 room templates (variations)
- [ ] Model 20 corridor templates
- [ ] Model 100 prop assets
- [ ] Create 50 decoration assets
- [ ] Create PBR materials (10-20)
- [ ] Set up modular kit in Blender
- [ ] Organize .blend files
- [ ] Document asset naming conventions

**Success Criteria:**
- Asset library supports diverse dungeon themes
- All assets use consistent scale (1 Blender unit = 1 meter)
- Materials are PBR-compliant
- Assets have proper LODs

---

### Phase 5: Gameplay Integration (2-3 weeks)

**Goal:** Add gameplay metadata and systems

**Tasks:**
- [ ] Implement spawner metadata in manifest
- [ ] Implement loot placement
- [ ] Implement zone tagging (entrance, main, boss)
- [ ] Add navmesh generation
- [ ] Add collision mesh generation
- [ ] Test monster AI pathfinding
- [ ] Test player navigation

**Success Criteria:**
- Monsters spawn correctly
- AI can navigate entire dungeon
- Loot placement makes sense
- Boss arenas are tagged correctly

---

### Phase 6: Procedural Variation (3-4 weeks)

**Goal:** Add procedural details for uniqueness

**Tasks:**
- [ ] Implement Geometry Nodes for prop scattering
- [ ] Add procedural damage/weathering
- [ ] Add procedural lighting (torches, braziers)
- [ ] Add procedural decorations (vines, rubble)
- [ ] Implement material variation (dirt, moss, cracks)
- [ ] Add procedural atmosphere (fog, particles)

**Success Criteria:**
- Two dungeons with same seed look identical
- Two dungeons with different seeds look unique
- Procedural elements enhance, not distract
- Performance stays within budget

---

### Phase 7: MMO Scale Testing (2-3 weeks)

**Goal:** Test at full MMO scale

**Tasks:**
- [ ] Generate 1000-room dungeon
- [ ] Test with 100+ concurrent players (simulation)
- [ ] Profile server load (dungeon generation)
- [ ] Profile client load (streaming)
- [ ] Optimize bottlenecks
- [ ] Add caching layer
- [ ] Add CDN for chunk delivery

**Success Criteria:**
- 1000-room dungeon generates in < 10 seconds
- Supports 100+ players per instance
- Chunks cached on CDN
- First-time load < 5 seconds

---

### Phase 8: Production Readiness (2-3 weeks)

**Goal:** Polish, optimization, tooling

**Tasks:**
- [ ] Build dungeon editor GUI
- [ ] Add preview system (quick WebGL render)
- [ ] Add dungeon versioning
- [ ] Add dungeon rating/curation system
- [ ] Implement telemetry
- [ ] Write documentation
- [ ] Create art guidelines
- [ ] Set up CI/CD pipeline

**Success Criteria:**
- Designers can create dungeons without code
- Preview system shows dungeon in < 1 second
- Telemetry captures player behavior
- Documentation covers all workflows

---

## Performance Targets

### Generation Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Graph generation | < 1s | 1000 rooms |
| Chunk subdivision | < 500ms | 400 chunks |
| Single chunk export | < 200ms | Blender GLB export |
| Batch chunk export | < 10s | All 400 chunks (parallel) |
| Full dungeon pipeline | < 10s | End-to-end |

### Runtime Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Chunk load time | < 100ms | From disk/cache |
| Chunk unload time | < 50ms | Cleanup |
| LOD switch time | < 16ms | 1 frame @ 60 FPS |
| Memory per chunk | < 10MB | Average |
| Total memory | < 4GB | All loaded chunks |
| Draw calls per chunk | < 50 | Batched |
| Frame rate | 60 FPS | 1080p, mid-range GPU |

### Scale Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Dungeon size | 1km × 1km | Max navigable area |
| Room count | 500-2000 | Varies by type |
| Unique assets | 200-500 | In asset library |
| Chunk count | 400 (20×20) | 50m grid |
| Poly budget | 5M tris | Visible at once |
| Texture budget | 2GB | All loaded textures |

---

## Tech Stack

### Orchestrator

**Language:** Python or Node.js  
**Dependencies:**
- `numpy` - Math and array operations
- `networkx` - Graph algorithms
- `redis` - Command queue
- `pydantic` - Data validation
- `msgpack` - Serialization (optional)

**Algorithms:**
- Wave Function Collapse (WFC)
- Binary Space Partitioning (BSP)
- Cellular Automata
- Voronoi Diagrams
- A* Pathfinding (connectivity validation)

---

### Blender Sidecar

**Language:** Python 3.11  
**Dependencies:**
- `bpy` - Blender Python API
- `redis` - Command consumer
- `msgpack` - Fast serialization

**Commands:**
- `LoadBlend` - Load asset library
- `CreateCollection` - Create hierarchy
- `InstanceCollection` - Instance rooms/corridors
- `AttachNodeGroup` - Add Geometry Nodes
- `ExportGLTF` - Export chunk to GLB
- `GenerateNavmesh` - Create navigation mesh

---

### Game Engine

**Options:**
- **Unity** (C#) - Good for MMOs, strong netcode
- **Unreal Engine** (C++/BP) - Best graphics, built-in streaming
- **Godot** (GDScript/C#) - Lightweight, open-source

**Required Systems:**
- Chunk streaming manager
- LOD manager
- Navmesh runtime
- Spawner system
- Collision system

---

## Example Workflows

### Workflow 1: Generate Test Dungeon

```bash
# 1. Start Blender sidecar
cd /Users/highlander/gamedev/blender
blender -b --python sidecar.py

# 2. Run orchestrator (separate terminal)
cd orchestrator
python generate_dungeon.py \
  --seed 12345 \
  --size 500 \
  --rooms 100 \
  --theme crypt \
  --output /tmp/dungeon_test_001
  
# Output:
# ✓ Graph generated (100 rooms, 150 corridors)
# ✓ Layout placed (bounds: 500x500m)
# ✓ Chunks subdivided (10x10 grid = 100 chunks)
# ✓ Sent 100 commands to Blender sidecar
# ✓ Exported 100 GLB files
# ✓ Generated manifest: /tmp/dungeon_test_001/manifest.json
# Total time: 8.3 seconds
```

---

### Workflow 2: Iterate on Single Room

```bash
# Test single room template in Blender
cd orchestrator
python test_single_room.py \
  --room-template rect_10x10_stone \
  --decorations high \
  --output /tmp/room_test.glb
  
# View in Blender
blender /tmp/room_test.glb
```

---

### Workflow 3: Preview Dungeon Layout

```bash
# Generate layout only (no geometry)
python generate_dungeon.py \
  --preview-only \
  --output /tmp/preview.png
  
# Opens 2D top-down map of dungeon layout
# Shows: rooms, corridors, connections, zones
```

---

### Workflow 4: Regenerate Single Chunk

```bash
# Regenerate chunk with different LOD
python regenerate_chunk.py \
  --dungeon-id crypt_001 \
  --chunk-coord 5,10 \
  --lod 0 \
  --output /build/dungeons/crypt_001/chunk_5_10_lod0.glb
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Set up project structure**
   ```bash
   mkdir -p orchestrator/algorithms
   mkdir -p orchestrator/dungeon_generator
   mkdir -p assets/dungeon_crypt
   mkdir -p build/dungeons
   ```

2. **Implement basic BSP algorithm**
   - Start with simple rectangular rooms
   - Generate 10-room dungeon
   - Output JSON manifest

3. **Create first room template**
   - Model simple 10×10m stone room
   - Add door sockets (north, south, east, west)
   - Export to `assets/dungeon_crypt/room_basic.blend`

4. **Test end-to-end pipeline**
   - Generate manifest → Send to Blender → Export GLB → Import in Unity/Unreal

### Medium-Term Goals (Month 1)

- Complete Phases 1-3 (POC, Small Dungeon, Streaming)
- Create 20 room templates
- Implement chunk streaming in game engine
- Profile performance

### Long-Term Goals (Months 2-3)

- Complete asset library (50+ rooms, 200+ props)
- Add Geometry Nodes for procedural details
- Implement MMO scale testing
- Polish and production readiness

---

## Success Metrics

### Technical Metrics
- ✅ Generate 1000-room dungeon in < 10 seconds
- ✅ Stream chunks at < 100ms each
- ✅ Maintain 60 FPS with 100+ players
- ✅ Memory under 4GB per instance

### Quality Metrics
- ✅ Dungeons feel handcrafted, not random
- ✅ Players can navigate entire dungeon
- ✅ No visual artifacts (gaps, z-fighting)
- ✅ Monster AI can path everywhere

### Business Metrics
- ✅ Designers can create new dungeon themes
- ✅ Players rate dungeons 4+ stars
- ✅ Dungeons are replayable (variation)
- ✅ Server costs stay under budget

---

## Resources

### Reference Implementations
- **Diablo 3** - BSP dungeon generation
- **Path of Exile** - WFC tile-based generation
- **Minecraft** - Chunk streaming system
- **WoW Classic** - Hand-crafted modular dungeons

### Algorithms
- [Wave Function Collapse](https://github.com/mxgmn/WaveFunctionCollapse)
- [BSP Dungeon Generation](http://www.roguebasin.com/index.php?title=Basic_BSP_Dungeon_generation)
- [Cellular Automata Caves](http://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels)

### Asset Creation
- [Modular Dungeon Kits (Unreal Marketplace)](https://www.unrealengine.com/marketplace/en-US/product/modular-dungeon)
- [Synty Studios Low Poly Dungeons](https://syntystore.com/products/polygon-dungeons-pack)

### Tools
- [Blender Geometry Nodes](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html)
- [Houdini Engine](https://www.sidefx.com/products/houdini-engine/) - Alternative to Blender
- [Unity Addressables](https://docs.unity3d.com/Packages/com.unity.addressables@latest) - Asset streaming

---

## Appendix: Command Reference

### Blender Sidecar Commands

```python
# Load asset library
LoadBlend(
    filepath="/assets/dungeon_crypt.blend",
    link=True,
    collections=["Rooms", "Corridors", "Props"]
)

# Create chunk collection
CreateCollection(
    name="chunk_5_10",
    parent="Scene"
)

# Instance room
InstanceCollection(
    collection="rect_10x10_stone",
    parent="chunk_5_10",
    name="room_42",
    transform={
        "position": [100, 200, 0],
        "rotation": [0, 0, 45],
        "scale": [1, 1, 1]
    }
)

# Attach Geometry Nodes for procedural details
AttachNodeGroup(
    object="chunk_5_10",
    node_group="NG_Scatter_Props",
    params={
        "density": 0.5,
        "seed": 12345,
        "scatter_on_surface": True
    }
)

# Export chunk
ExportGLTF(
    filepath="/build/dungeons/crypt_001/chunk_5_10.glb",
    selection=["chunk_5_10"],
    export_format="GLB",
    export_materials=True,
    export_cameras=False,
    export_lights=False
)
```

---

**Last Updated:** October 5, 2025  
**Status:** Planning Phase → Ready for Implementation  
**Next Milestone:** Phase 1 - Proof of Concept (2 weeks)

