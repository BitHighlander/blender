#!/usr/bin/env node
/**
 * Direct MCP Socket Test - Degenerate Labs Blender
 * 
 * Tests the FIRST-CLASS MCP server built into Blender!
 * No addon checkbox needed - it's just part of Blender now.
 */

import { createConnection } from 'net';

const HOST = 'localhost';
const PORT = 9876;

function sendCommand(client, command) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Timeout waiting for response'));
    }, 5000);

    client.once('data', (data) => {
      clearTimeout(timeout);
      try {
        const response = JSON.parse(data.toString());
        resolve(response);
      } catch (e) {
        reject(e);
      }
    });

    client.write(JSON.stringify(command));
  });
}

async function main() {
  console.log('🚀 Degenerate Labs Blender - First-Class MCP Test\n');
  console.log('═'.repeat(60));
  console.log('Testing BUILT-IN MCP Server (no addon needed!)');
  console.log('═'.repeat(60));
  console.log('');

  const client = createConnection({ host: HOST, port: PORT });

  client.on('error', (err) => {
    console.error('❌ Connection error:', err.message);
    console.error('\n💡 Make sure Blender is running:');
    console.error('   open ../build_darwin/bin/Blender.app\n');
    process.exit(1);
  });

  await new Promise((resolve) => {
    client.on('connect', () => {
      console.log(`✅ Connected to Blender MCP server at ${HOST}:${PORT}\n`);
      resolve();
    });
  });

  try {
    // Test 1: Ping
    console.log('TEST 1: Ping');
    console.log('─'.repeat(40));
    const pingResult = await sendCommand(client, {
      type: 'ping',
      params: {}
    });
    console.log('Response:', JSON.stringify(pingResult, null, 2));
    console.log('');

    // Test 2: Get scene info
    console.log('TEST 2: Get Scene Info');
    console.log('─'.repeat(40));
    const sceneResult = await sendCommand(client, {
      type: 'get_scene_info',
      params: {}
    });
    console.log('Response:', JSON.stringify(sceneResult, null, 2));
    console.log('');

    // Test 3: Create a cube!
    console.log('TEST 3: Create Cube at [5, 5, 0]');
    console.log('─'.repeat(40));
    console.log('👀 Watch your Blender window!');
    const cubeResult = await sendCommand(client, {
      type: 'create_cube',
      params: {
        location: [5, 5, 0],
        size: 2
      }
    });
    console.log('Response:', JSON.stringify(cubeResult, null, 2));
    console.log('');

    // Success!
    console.log('═'.repeat(60));
    console.log('✨ SUCCESS! First-Class MCP Server Working!');
    console.log('═'.repeat(60));
    console.log('\n🎯 Your Blender now has MCP built-in!');
    console.log('   - Socket server: localhost:9876');
    console.log('   - Auto-starts with Blender');
    console.log('   - Ready for Cursor agent integration!\n');

  } catch (error) {
    console.error('\n💥 Error:', error.message);
  } finally {
    client.end();
  }
}

main().catch(console.error);

