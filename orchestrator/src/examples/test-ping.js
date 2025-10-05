/**
 * Test Ping Command
 * 
 * Simple test to verify the Blender sidecar is responsive.
 */

import { BlenderClient } from '../lib/blender-client.js';

async function main() {
  console.log('='.repeat(60));
  console.log('Testing Blender Sidecar Connection');
  console.log('='.repeat(60));
  console.log('');

  const client = new BlenderClient();

  try {
    console.log('Sending Ping command...');
    const response = await client.ping('Hello from Node.js orchestrator!');

    console.log('');
    console.log('✅ Response received:');
    console.log('');
    console.log('  Blender Version:', response.result.blender_version);
    console.log('  Sidecar Version:', response.result.sidecar_version);
    console.log('  Worker ID:', response.result.worker_id);
    console.log('  Echo:', response.result.echo);
    console.log('');
    console.log('  Metrics:');
    console.log('    CPU Time:', response.metrics.cpu_ms, 'ms');
    console.log('    Wall Time:', response.metrics.wall_ms, 'ms');
    console.log('');
    console.log('='.repeat(60));
    console.log('✅ SUCCESS: Orchestrator ↔ Blender communication working!');
    console.log('='.repeat(60));

  } catch (error) {
    console.error('');
    console.error('❌ ERROR:', error.message);
    console.error('');
    console.error('Make sure:');
    console.error('  1. Redis is running (redis-server)');
    console.error('  2. Blender is open with sidecar running');
    console.error('');
    process.exit(1);
  } finally {
    await client.close();
  }
}

main();

