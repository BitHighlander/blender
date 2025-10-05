/**
 * Test CreateCube Command
 * 
 * Creates a simple cube in Blender to verify mesh creation.
 */

import { BlenderClient } from '../lib/blender-client.js';

async function main() {
  console.log('='.repeat(60));
  console.log('Testing CreateCube Command');
  console.log('='.repeat(60));
  console.log('');

  const client = new BlenderClient();

  try {
    console.log('Creating cube at origin...');
    const response = await client.createCube({
      name: 'TestCube',
      location: [0, 0, 0],
      size: 2.0
    });

    console.log('');
    console.log('✅ Cube created successfully!');
    console.log('');
    console.log('  Object:', response.result.object_name);
    console.log('  Location:', response.result.location);
    console.log('  Size:', response.result.size);
    console.log('  Vertices:', response.result.vertices);
    console.log('  Faces:', response.result.faces);
    console.log('');
    console.log('👀 Check your Blender window - you should see a cube!');
    console.log('');

  } catch (error) {
    console.error('');
    console.error('❌ ERROR:', error.message);
    console.error('');
    process.exit(1);
  } finally {
    await client.close();
  }
}

main();

