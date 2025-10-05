#!/bin/bash
# Start Degenerate Labs Blender Sidecar
# This runs your custom-built Blender in headless mode with the sidecar active

BLENDER_BIN="../build_darwin/bin/Blender.app/Contents/MacOS/Blender"

echo "🚀 Starting Degenerate Labs Blender Sidecar"
echo "============================================"
echo ""
echo "📍 Blender binary: $BLENDER_BIN"
echo "📦 Sidecar version: 2.0.0-realtime"
echo "🔄 Threading: bpy.app.timers (non-blocking)"
echo ""
echo "🎮 Starting Blender in headless mode..."
echo "   (The sidecar will keep Blender responsive!)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Blender in background mode with sidecar
"$BLENDER_BIN" -b --python sidecar.py

