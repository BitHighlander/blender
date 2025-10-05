# Configuration Guide

This document explains how to configure the Blender sidecar for different environments.

---

## Configuration Sources

The sidecar supports multiple configuration sources (in order of precedence):

1. **Environment Variables** (highest priority)
2. **`.env` file** in project root
3. **`sidecar.toml`** configuration file
4. **Default values** (lowest priority)

---

## Environment Variables

### Development Setup (Localhost)

For local development, you can hardcode Redis to `localhost:6379`:

```bash
# No configuration needed - defaults to localhost
blender -b --python sidecar.py
```

### Production Setup (.env)

Create a `.env` file in the project root:

```bash
# .env
REDIS_URL=redis://:password@redis-prod.example.com:6379/0
REDIS_CMD_STREAM=blender:cmd
REDIS_REPLY_STREAM=blender:reply
REDIS_CONSUMER_GROUP=cg:prod
REDIS_CONSUMER_NAME=worker-01

SIDECAR_WORKER_ID=worker-01
SIDECAR_LOG_LEVEL=INFO

PATHS_ASSETS_ROOT=/mnt/assets
PATHS_BUILD_ROOT=/mnt/build
PATHS_TMP_ROOT=/tmp/sidecar

FEATURES_USE_ZSTD=true
FEATURES_USE_MSGPACK=true
FEATURES_ALLOW_OPS_FALLBACK=false

LIMITS_MAX_OBJECTS=200000
LIMITS_MAX_GLB_MB=500
LIMITS_CMD_TIMEOUT_MS=600000
```

### Docker Environment

```bash
docker run \
  -e REDIS_URL=redis://redis:6379/0 \
  -e SIDECAR_WORKER_ID=worker-docker-01 \
  -v /data/assets:/mnt/assets:ro \
  -v /data/build:/mnt/build \
  blender-sidecar:latest
```

---

## Configuration File (sidecar.toml)

Alternatively, use a TOML configuration file:

```toml
# sidecar.toml

[redis]
url = "redis://:password@host:6379/0"
cmd_stream = "blender:cmd"
reply_stream_default = "blender:reply"
events_stream = "blender:events"
metrics_stream = "blender:metrics"
health_key_prefix = "blender:health"
consumer_group = "cg:prod"
consumer_name = "worker-01"

[sidecar]
worker_id = "worker-01"
log_level = "INFO"
version = "1.0.0"

[paths]
assets_root = "/mnt/assets"
build_root = "/mnt/build"
tmp_root = "/tmp/sidecar"

# Path allowlist (security)
allowed_read_paths = [
    "/mnt/assets",
    "/mnt/build",
]
allowed_write_paths = [
    "/mnt/build",
    "/tmp/sidecar",
]

[features]
use_zstd = true
use_msgpack = true
allow_ops_fallback = false  # Disable UI operators in headless mode
enable_profiling = false     # Enable detailed per-phase timings
enable_tracing = true        # Trace/span ID correlation

[limits]
max_objects = 200000         # Max objects per scene
max_glb_mb = 500             # Max export file size
cmd_timeout_ms = 600000      # 10 minutes
heartbeat_interval_sec = 5
max_batch_ops = 1000         # Max operations in a Batch command

[blender]
disable_undo = true          # Disable global undo during operations
startup_blend = ""           # Optional: path to startup .blend file
temp_blend_prefix = "sidecar_"
```

---

## Configuration Reference

### Redis Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `url` | string | `redis://localhost:6379/0` | Redis connection URL |
| `cmd_stream` | string | `blender:cmd` | Command ingress stream |
| `reply_stream_default` | string | `blender:reply` | Default reply stream |
| `events_stream` | string | `blender:events` | Structured events stream |
| `metrics_stream` | string | `blender:metrics` | Metrics stream |
| `health_key_prefix` | string | `blender:health` | Health key prefix |
| `consumer_group` | string | `cg:default` | Consumer group name |
| `consumer_name` | string | hostname | Consumer name (unique per worker) |

### Sidecar Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `worker_id` | string | hostname | Unique worker identifier |
| `log_level` | string | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `version` | string | `1.0.0` | Sidecar version |

### Paths Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `assets_root` | string | `/mnt/assets` | Root directory for read-only assets |
| `build_root` | string | `/mnt/build` | Root directory for build outputs |
| `tmp_root` | string | `/tmp/sidecar` | Temporary workspace directory |
| `allowed_read_paths` | array | (see above) | Security: allowed read directories |
| `allowed_write_paths` | array | (see above) | Security: allowed write directories |

### Features Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_zstd` | bool | `true` | Enable Zstandard compression |
| `use_msgpack` | bool | `true` | Enable MessagePack encoding |
| `allow_ops_fallback` | bool | `false` | Allow UI operators as fallback |
| `enable_profiling` | bool | `false` | Enable detailed profiling |
| `enable_tracing` | bool | `true` | Enable trace/span correlation |

### Limits Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_objects` | int | `200000` | Max objects per scene |
| `max_glb_mb` | int | `500` | Max export file size (MB) |
| `cmd_timeout_ms` | int | `600000` | Command timeout (10 min) |
| `heartbeat_interval_sec` | int | `5` | Heartbeat update interval |
| `max_batch_ops` | int | `1000` | Max ops in Batch command |

### Blender Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `disable_undo` | bool | `true` | Disable undo during operations |
| `startup_blend` | string | empty | Optional startup .blend file |
| `temp_blend_prefix` | string | `sidecar_` | Prefix for temp .blend files |

---

## Development Defaults

For local development, the sidecar uses these defaults if no config is provided:

```python
DEFAULT_CONFIG = {
    "redis": {
        "url": "redis://localhost:6379/0",
        "cmd_stream": "blender:cmd",
        "reply_stream_default": "blender:reply",
        "events_stream": "blender:events",
        "metrics_stream": "blender:metrics",
        "health_key_prefix": "blender:health",
        "consumer_group": "cg:dev",
        "consumer_name": f"worker-{socket.gethostname()}",
    },
    "sidecar": {
        "worker_id": socket.gethostname(),
        "log_level": "DEBUG",  # Verbose for dev
        "version": "1.0.0-dev",
    },
    "paths": {
        "assets_root": "./assets",
        "build_root": "./build",
        "tmp_root": "./tmp",
    },
    "features": {
        "use_zstd": False,  # Disabled for easier debugging
        "use_msgpack": False,
        "allow_ops_fallback": True,  # Permissive in dev
        "enable_profiling": True,
        "enable_tracing": True,
    },
    "limits": {
        "max_objects": 10000,  # Lower for dev
        "max_glb_mb": 100,
        "cmd_timeout_ms": 60000,  # 1 min
        "heartbeat_interval_sec": 10,
        "max_batch_ops": 100,
    },
}
```

---

## Loading Configuration

The sidecar loads configuration in this order:

```python
# 1. Load defaults
config = load_defaults()

# 2. Merge sidecar.toml (if exists)
if os.path.exists("sidecar.toml"):
    config.merge(load_toml("sidecar.toml"))

# 3. Merge .env (if exists)
if os.path.exists(".env"):
    load_dotenv(".env")

# 4. Override with environment variables
config.merge(load_from_env())
```

---

## Example Setups

### Setup 1: Local Development (Hello World)

```bash
# Just run it - uses localhost defaults
blender -b --python sidecar.py
```

### Setup 2: Staging Environment

```bash
# .env.staging
REDIS_URL=redis://:stagingpass@redis-staging:6379/0
REDIS_CONSUMER_GROUP=cg:staging
SIDECAR_WORKER_ID=staging-worker-01
SIDECAR_LOG_LEVEL=INFO

# Run
cp .env.staging .env
blender -b --python sidecar.py
```

### Setup 3: Production (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  sidecar:
    image: blender-sidecar:latest
    environment:
      REDIS_URL: redis://redis:6379/0
      REDIS_CONSUMER_GROUP: cg:prod
      SIDECAR_WORKER_ID: worker-${HOSTNAME}
      PATHS_ASSETS_ROOT: /assets
      PATHS_BUILD_ROOT: /build
    volumes:
      - ./assets:/assets:ro
      - ./build:/build
    depends_on:
      - redis
    deploy:
      replicas: 4  # 4 workers for parallelism

volumes:
  redis-data:
```

### Setup 4: Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blender-sidecar
spec:
  replicas: 10
  selector:
    matchLabels:
      app: blender-sidecar
  template:
    metadata:
      labels:
        app: blender-sidecar
    spec:
      containers:
      - name: sidecar
        image: blender-sidecar:1.0.0
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: REDIS_CONSUMER_GROUP
          value: "cg:k8s-prod"
        - name: SIDECAR_WORKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: assets
          mountPath: /mnt/assets
          readOnly: true
        - name: build
          mountPath: /mnt/build
        resources:
          limits:
            memory: "4Gi"
            cpu: "2"
          requests:
            memory: "2Gi"
            cpu: "1"
      volumes:
      - name: assets
        persistentVolumeClaim:
          claimName: assets-pvc
      - name: build
        persistentVolumeClaim:
          claimName: build-pvc
```

---

## Validation

The sidecar validates configuration on startup:

```python
# Validates:
# - Redis URL is reachable
# - Paths exist and are accessible
# - Limits are within reasonable bounds
# - Feature flags are compatible
# - Worker ID is unique in consumer group
```

If validation fails, the sidecar exits with a detailed error message.

---

## Debugging Configuration

Set `SIDECAR_LOG_LEVEL=DEBUG` to see full config on startup:

```bash
SIDECAR_LOG_LEVEL=DEBUG blender -b --python sidecar.py
```

Output:

```
[DEBUG] Loaded configuration:
{
  "redis": {
    "url": "redis://localhost:6379/0",
    "cmd_stream": "blender:cmd",
    ...
  },
  "sidecar": {
    "worker_id": "my-laptop",
    ...
  }
}
[INFO] Redis connected: localhost:6379
[INFO] Consumer group: cg:dev
[INFO] Worker ID: my-laptop
[INFO] Waiting for commands on blender:cmd...
```

---

## Security Best Practices

1. **Never commit `.env` files** with production credentials
2. **Use Redis AUTH** in production (`redis://:password@host:port/db`)
3. **Restrict path allowlists** to minimum required directories
4. **Disable `allow_ops_fallback`** in production (headless operators can be unsafe)
5. **Use TLS for Redis** in production (`rediss://...`)
6. **Rotate worker IDs** to prevent consumer name collisions

---

## Next Steps

- See `SPEC.md` for full command documentation
- See `ROADMAP.md` for implementation plan
- See `examples/` for sample configurations

