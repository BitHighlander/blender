#!/usr/bin/env node
/**
 * MCP Bridge for Cursor IDE
 * 
 * Bridges Cursor's stdio-based MCP client to Blender's socket-based MCP server.
 * Cursor spawns this script and communicates via stdin/stdout.
 * This script connects to Blender's MCP socket (port 9876) and bridges the communication.
 */

import { createConnection } from 'net';

const BLENDER_HOST = 'localhost';
const BLENDER_PORT = 9876;

let socket = null;
let connected = false;

// Connect to Blender MCP server
function connect() {
  socket = createConnection({ host: BLENDER_HOST, port: BLENDER_PORT });

  socket.on('connect', () => {
    console.error('✅ Connected to Blender MCP');
    connected = true;
  });

  socket.on('data', (data) => {
    // Forward Blender response to Cursor (stdout)
    process.stdout.write(data.toString() + '\n');
  });

  socket.on('error', (err) => {
    console.error('❌ Blender MCP error:', err.message);
    process.exit(1);
  });

  socket.on('close', () => {
    console.error('🔌 Disconnected from Blender MCP');
    process.exit(0);
  });
}

// Listen for commands from Cursor (stdin)
process.stdin.on('data', (data) => {
  if (connected && socket) {
    // Forward Cursor command to Blender
    socket.write(data);
  }
});

process.stdin.on('end', () => {
  if (socket) {
    socket.end();
  }
  process.exit(0);
});

// Start
connect();

