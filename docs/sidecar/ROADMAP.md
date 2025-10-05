# Blender Sidecar Implementation Roadmap

**Version:** 1.0  
**Last Updated:** October 5, 2025

This roadmap breaks down the sidecar implementation into testable, incremental milestones. Each milestone is self-contained and verifiable.

---

## Milestone 0: Hello World (Foundation) ✨

**Goal:** Prove the basic infrastructure works—Blender starts, Redis connects, one command round-trips.

### Tasks

- [x] Create project structure
- [ ] Set up Redis Streams consumer in Python
- [ ] Implement basic command router
- [ ] Implement `Ping` command
- [ ] Test: Send `Ping` from Redis CLI, get response back

### Success Criteria

```bash
# Terminal 1: Start Redis
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Start sidecar
blender -b --python sidecar.py

# Terminal 3: Send command
redis-cli XADD blender:cmd "*" payload '{"v":"1.0","cmd":"Ping","params":{"echo":"hello"},"trace_id":"test-001"}'

# Expected: Response in blender:reply stream with echo="hello"
redis-cli XREAD STREAMS blender:reply 0
```

**Deliverables:**
- `sidecar.py` — main entry point
- `sidecar/consumer.py` — Redis Streams consumer
- `sidecar/router.py` — command dispatcher
- `sidecar/commands/ping.py` — Ping handler
- `sidecar/config.py` — configuration loader
- `.env.example` — example environment variables
- `requirements.txt` — Python dependencies

**Estimated Time:** 1-2 days

---

## Milestone 1: Core Commands (Vertical Slice)

**Goal:** Implement the minimal command set for a complete dungeon export flow.

### Phase 1A: Scene Management

- [ ] `GetCapabilities` — return Blender version, available features
- [ ] `CreateScene` — create new scene with custom name and settings
- [ ] `GetSceneSummary` — return counts, memory, bounding box
- [ ] Test: Create scene, verify summary

### Phase 1B: Asset Loading & Collections

- [ ] `LoadBlend` — link external .blend file collections
- [ ] `CreateCollection` — create empty collection hierarchy
- [ ] Test: Load test asset pack, verify collections exist

### Phase 1C: Instancing

- [ ] `InstanceCollection` — single instance with transform
- [ ] `InstanceCollectionMany` — vectorized batch instancing
- [ ] Test: Instance 100 objects, verify positions

### Phase 1D: Export

- [ ] `ExportGLTF` — export selection to .glb file
- [ ] `WriteManifest` — generate JSON manifest with transforms/metadata
- [ ] Test: Export test scene, verify .glb file hash

### Success Criteria

Complete this flow end-to-end:

```python
# Pseudo-code (sent as Redis commands)
CreateScene(name="test_001")
LoadBlend(filepath="assets/test_pack.blend", collections=["Cubes"])
CreateCollection(name="INSTANCES", parent="Scene")
InstanceCollectionMany(
    parent_collection="INSTANCES",
    items=[
        {"collection": "Cubes", "name": "cube_0", "transform": {"pos": [0,0,0]}},
        {"collection": "Cubes", "name": "cube_1", "transform": {"pos": [2,0,0]}},
    ]
)
ExportGLTF(filepath="/tmp/test_001.glb", selection=["INSTANCES"])
WriteManifest(filepath="/tmp/test_001.manifest.json")
```

**Deliverables:**
- `sidecar/commands/scene.py`
- `sidecar/commands/collections.py`
- `sidecar/commands/export.py`
- `tests/test_vertical_slice.py`
- Golden test asset: `assets/test_pack.blend`

**Estimated Time:** 3-5 days

---

## Milestone 2: Geometry Nodes Integration

**Goal:** Enable parametric geometry via Geometry Nodes modifiers.

### Tasks

- [ ] `AttachNodeGroup` — add GN modifier to object
- [ ] `SetNodeParams` — update GN input parameters
- [ ] `SetNamedAttributes` — set named attributes on geometry
- [ ] `EvaluateDepsgraph` — force evaluation, return timing
- [ ] Test: Attach GN modifier, set params, export, verify geometry changes

### Success Criteria

```python
CreateScene(name="gn_test")
CreateMeshFromSpec(name="base_mesh", type="plane", size=10)
AttachNodeGroup(object="base_mesh", node_group="NG_Subdivide", modifier_name="GN_Mod")
SetNodeParams(object="base_mesh", modifier="GN_Mod", params={"levels": 3})
EvaluateDepsgraph()
ExportGLTF(filepath="/tmp/gn_test.glb", selection=["base_mesh"])
```

**Deliverables:**
- `sidecar/commands/geometry_nodes.py`
- `tests/test_geometry_nodes.py`
- Test asset: `assets/test_nodegroups.blend`

**Estimated Time:** 2-3 days

---

## Milestone 3: Observability & Error Handling

**Goal:** Production-ready logging, metrics, and error propagation.

### Tasks

- [ ] Structured event stream (`blender:events`)
- [ ] Metrics collection (`blender:metrics`)
- [ ] Health heartbeat (`blender:health:<worker_id>`)
- [ ] Error code standardization
- [ ] `GetLastError` command
- [ ] Trace/span ID propagation
- [ ] Test: Trigger error, verify structured error response

### Success Criteria

- Every command emits `start` and `finish` events
- Metrics include: `cpu_ms`, `wall_ms`, `mem_mb`, `depsgraph_updates`
- Errors include: `code`, `message`, `details`, `retryable`
- Heartbeat updates every 5 seconds

**Deliverables:**
- `sidecar/telemetry.py`
- `sidecar/errors.py`
- `tests/test_telemetry.py`

**Estimated Time:** 2-3 days

---

## Milestone 4: Performance & Batching

**Goal:** Optimize for throughput and large scenes.

### Tasks

- [ ] `Batch` command — execute multiple ops atomically
- [ ] MessagePack support for params
- [ ] Zstandard compression for large payloads
- [ ] Path allowlist security
- [ ] Resource limits (max objects, timeout)
- [ ] Test: Batch 1000 instances in one command

### Success Criteria

- `Batch` command executes 100+ ops in <1s
- Compression reduces payload size by >50% for large data
- Sidecar respects memory/timeout limits

**Deliverables:**
- `sidecar/commands/batch.py`
- `sidecar/compression.py`
- `sidecar/limits.py`
- `tests/test_batching.py`
- `tests/test_performance.py`

**Estimated Time:** 2-4 days

---

## Milestone 5: Full Command Set

**Goal:** Implement all remaining commands from spec.

### Phase 5A: Scene Lifecycle

- [ ] `SaveBlend`
- [ ] `PurgeOrphans`
- [ ] `CleanupTemp`

### Phase 5B: Object Operations

- [ ] `CreateMeshFromSpec`
- [ ] `SetCustomProps`

### Phase 5C: Evaluation

- [ ] `RealizeInstances`

### Phase 5D: Import

- [ ] `ImportGLB`
- [ ] `AssignMaterialPreset`

### Success Criteria

All commands in spec implemented and tested.

**Deliverables:**
- Complete command implementations
- Full test coverage
- API documentation for each command

**Estimated Time:** 3-5 days

---

## Milestone 6: Production Readiness

**Goal:** Deploy-ready sidecar with CI/CD and operational tooling.

### Tasks

- [ ] Docker container with Blender + sidecar
- [ ] CI/CD pipeline (GitHub Actions / GitLab CI)
- [ ] Golden tests (deterministic exports)
- [ ] Soak tests (memory leaks, stability)
- [ ] Fault injection tests
- [ ] Deployment documentation
- [ ] Monitoring dashboard (Grafana/Prometheus)

### Success Criteria

- CI runs golden tests, all pass
- Soak test runs 10,000 commands with no memory growth
- Docker image < 500MB
- Documentation includes deployment playbook

**Deliverables:**
- `Dockerfile`
- `.github/workflows/ci.yml`
- `tests/golden/` — golden test fixtures
- `tests/soak_test.py`
- `docs/sidecar/DEPLOYMENT.md`
- `docs/sidecar/MONITORING.md`

**Estimated Time:** 5-7 days

---

## Milestone 7: Advanced Features (Optional)

**Goal:** Nice-to-have features for power users.

### Potential Features

- [ ] Multi-scene support (parallel scene operations)
- [ ] Incremental exports (delta updates)
- [ ] Live preview WebSocket stream
- [ ] Render commands (Cycles/Eevee headless renders)
- [ ] Animation baking
- [ ] Physics simulation
- [ ] Custom Python script execution (sandboxed)

**Estimated Time:** Variable (1-2 weeks per feature)

---

## Testing Strategy Summary

### Test Levels

1. **Unit Tests**: Mock bpy, test command logic in isolation
2. **Integration Tests**: Real Blender + Redis (local)
3. **Golden Tests**: Deterministic outputs (hash verification)
4. **Soak Tests**: Long-running stability (10k+ commands)
5. **Fault Tests**: Simulate failures (network, disk, OOM)

### Test Assets

Create minimal test assets:
- `test_pack.blend` — simple cubes/planes for instancing
- `test_nodegroups.blend` — basic GN node groups
- `test_materials.blend` — PBR material presets

### CI Pipeline

```yaml
# .github/workflows/ci.yml
test:
  - Start Redis container
  - Install Blender (headless)
  - Run unit tests (pytest)
  - Run integration tests
  - Run golden tests (compare hashes)
  - Upload artifacts (logs, exports)
```

---

## Development Environment Setup

### Prerequisites

- Blender 4.2+ (headless build)
- Python 3.11+
- Redis 7+ (local or Docker)
- Git

### Quick Start

```bash
# 1. Clone repo
git clone <repo-url>
cd blender-sidecar

# 2. Install Python deps
pip install -r requirements.txt

# 3. Start Redis (Docker)
docker run -d -p 6379:6379 --name redis-dev redis:7-alpine

# 4. Run sidecar
blender -b --python sidecar.py

# 5. Send test command (separate terminal)
python tests/send_ping.py
```

---

## Progress Tracking

- [ ] Milestone 0: Hello World (Foundation)
- [ ] Milestone 1: Core Commands (Vertical Slice)
- [ ] Milestone 2: Geometry Nodes Integration
- [ ] Milestone 3: Observability & Error Handling
- [ ] Milestone 4: Performance & Batching
- [ ] Milestone 5: Full Command Set
- [ ] Milestone 6: Production Readiness
- [ ] Milestone 7: Advanced Features (Optional)

---

## Success Metrics

### Technical Metrics

- **Latency**: P50 < 100ms for simple commands, P99 < 1s
- **Throughput**: 100+ commands/sec per worker
- **Memory**: Stable memory usage over 24h soak test
- **Reliability**: 99.9% command success rate

### Business Metrics

- Export time for 1000-room dungeon: < 10s
- Golden test stability: 100% reproducible outputs
- Developer onboarding: < 30 min to first command

---

## Notes

- Focus on Milestone 0 first—prove the concept works
- Each milestone should be demo-able and testable
- Prioritize correctness over performance initially
- Keep scope minimal—orchestrator handles game logic

