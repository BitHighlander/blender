#!/usr/bin/env node
/**
 * Test MCP Connection
 * 
 * Simple test to verify the orchestrator can talk to Blender via MCP socket
 */

import { MCPClient } from '../lib/mcp-client.js';

async function main() {
  console.log('🧪 Testing MCP Connection\n');

  const client = new MCPClient('localhost', 9876);

  try {
    // Connect
    await client.connect();

    // Test 1: Ping
    console.log('TEST 1: Ping');
    console.log('─'.repeat(40));
    const pingResult = await client.ping();
    console.log('✅ Result:', pingResult.result);
    console.log('');

    // Test 2: Get scene info
    console.log('TEST 2: Get Scene Info');
    console.log('─'.repeat(40));
    const sceneResult = await client.getSceneInfo();
    console.log('✅ Result:', sceneResult.result);
    console.log('');

    // Test 3: Create a cube
    console.log('TEST 3: Create Cube');
    console.log('─'.repeat(40));
    const cubeResult = await client.createCube({
      location: [2, 2, 0],
      size: 1.5,
    });
    console.log('✅ Result:', cubeResult.result);
    console.log('');

    console.log('═'.repeat(40));
    console.log('✨ All tests passed!');
    console.log('═'.repeat(40));

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  } finally {
    await client.close();
  }
}

main();

