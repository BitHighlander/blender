#!/bin/bash
# Start Blender with GUI and sidecar
# This lets you SEE the dungeon being built in real-time!

BLENDER_BIN="/Users/highlander/gamedev/build_darwin/bin/Blender.app/Contents/MacOS/Blender"

echo "🚀 Starting Degenerate Labs Blender with GUI + Sidecar"
echo "======================================================="
echo ""
echo "📍 Blender binary: $BLENDER_BIN"
echo "📦 Sidecar version: 2.0.0-realtime"
echo "🔄 Threading: bpy.app.timers (non-blocking)"
echo ""
echo "🎮 Starting Blender WITH GUI..."
echo "   You'll see the dungeon build in REAL-TIME!"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Blender WITH GUI and autoload sidecar
"$BLENDER_BIN" --python /Users/highlander/gamedev/blender/sidecar.py

