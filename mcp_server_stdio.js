#!/usr/bin/env node
/**
 * MCP STDIO Bridge for Cursor
 * 
 * Cursor spawns this as a stdio-based MCP server.
 * This bridges to Blender's socket MCP server.
 */

import { createConnection } from 'net';

const BLENDER_HOST = process.env.BLENDER_HOST || 'localhost';
const BLENDER_PORT = parseInt(process.env.BLENDER_PORT || '9876');

let socket = null;

// Connect to Blender
socket = createConnection({ host: BLENDER_HOST, port: BLENDER_PORT });

socket.on('connect', () => {
  console.error(`[MCP Bridge] Connected to Blender (${BLENDER_HOST}:${BLENDER_PORT})`);
});

socket.on('data', (data) => {
  // Blender → Cursor (stdout)
  process.stdout.write(data);
});

socket.on('error', (err) => {
  console.error(`[MCP Bridge] Error: ${err.message}`);
  process.exit(1);
});

socket.on('close', () => {
  console.error('[MCP Bridge] Disconnected');
  process.exit(0);
});

// Cursor → Blender (stdin)
process.stdin.on('data', (data) => {
  if (socket && socket.writable) {
    socket.write(data);
  }
});

process.stdin.on('end', () => {
  if (socket) socket.end();
  process.exit(0);
});

// Handle signals
process.on('SIGINT', () => {
  if (socket) socket.end();
  process.exit(0);
});

process.on('SIGTERM', () => {
  if (socket) socket.end();
  process.exit(0);
});

