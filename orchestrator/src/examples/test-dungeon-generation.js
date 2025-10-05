#!/usr/bin/env node
/**
 * Dungeon Generation Script - Example Workflow
 * 
 * This demonstrates the complete workflow for procedural dungeon generation
 * using the Blender Redis Bridge.
 * 
 * Run: node src/examples/test-dungeon-generation.js
 */

import { BlenderClient } from '../lib/blender-client.js';

console.log('🏰 Dungeon Generation Workflow - Learning Example\n');
console.log('═'.repeat(70));
console.log('This script demonstrates the complete dungeon generation workflow:');
console.log('  1. Verify Blender connection');
console.log('  2. Clear existing scene');
console.log('  3. Generate dungeon layout');
console.log('  4. Add decorations and lights');
console.log('  5. Setup camera and render settings');
console.log('  6. Export to game-ready format');
console.log('═'.repeat(70));
console.log('');

const client = new BlenderClient({
  redisHost: 'localhost',
  redisPort: 6379,
  timeout: 15000, // 15 seconds for complex operations
});

async function main() {
  try {
    // ═══════════════════════════════════════════════════════════════════
    // STEP 1: Verify Connection
    // ═══════════════════════════════════════════════════════════════════
    console.log('STEP 1: Verify Blender Connection');
    console.log('─'.repeat(70));
    
    const pingResult = await client.ping('Dungeon Generator v1.0');
    console.log('✅ Connected to Blender');
    console.log(`   Version: ${pingResult.result.blender_version}`);
    console.log(`   Sidecar: ${pingResult.result.sidecar_version}`);
    console.log(`   Worker: ${pingResult.result.worker_id}`);
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // STEP 2: Define Dungeon Parameters
    // ═══════════════════════════════════════════════════════════════════
    console.log('STEP 2: Configure Dungeon Parameters');
    console.log('─'.repeat(70));
    
    const dungeonConfig = {
      // Layout
      size: 15,           // Grid size (15x15)
      rooms: 8,           // Number of rooms
      
      // Style
      style: 'medieval',  // 'medieval', 'sci-fi', or 'fantasy'
      theme: 'dark',      // 'dark' or 'light'
      
      // Features
      add_lights: true,
      add_player: true,
      add_decorations: true,
      add_enemies: false, // Future feature
      
      // Room constraints
      min_room_size: 4,
      max_room_size: 8,
      corridor_width: 2,
    };
    
    console.log('📋 Dungeon Configuration:');
    console.log(`   Grid Size: ${dungeonConfig.size}x${dungeonConfig.size}`);
    console.log(`   Rooms: ${dungeonConfig.rooms}`);
    console.log(`   Style: ${dungeonConfig.style} (${dungeonConfig.theme})`);
    console.log(`   Features: Lights=${dungeonConfig.add_lights}, Player=${dungeonConfig.add_player}`);
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // STEP 3: Generate Dungeon
    // ═══════════════════════════════════════════════════════════════════
    console.log('STEP 3: Generate Dungeon Layout');
    console.log('─'.repeat(70));
    console.log('🔨 Building dungeon... (this may take a few seconds)');
    
    const startTime = Date.now();
    
    const dungeonResult = await client.sendCommand('CreateDungeon', dungeonConfig);
    
    const buildTime = Date.now() - startTime;
    
    console.log('✅ Dungeon generated successfully!');
    console.log(`   Name: ${dungeonResult.result.dungeon_name}`);
    console.log(`   Rooms: ${dungeonResult.result.rooms_created}`);
    console.log(`   Total Objects: ${dungeonResult.result.objects_created.length}`);
    console.log(`   Build Time: ${buildTime}ms`);
    console.log('');
    
    // Log first 5 objects as example
    console.log('📦 Sample Objects Created:');
    dungeonResult.result.objects_created.slice(0, 5).forEach((obj, i) => {
      console.log(`   ${i + 1}. ${obj}`);
    });
    if (dungeonResult.result.objects_created.length > 5) {
      console.log(`   ... and ${dungeonResult.result.objects_created.length - 5} more`);
    }
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // STEP 4: Get Dungeon Statistics
    // ═══════════════════════════════════════════════════════════════════
    console.log('STEP 4: Analyze Dungeon Statistics');
    console.log('─'.repeat(70));
    
    const statsResult = await client.sendCommand('GetDungeonStats', {});
    
    console.log('📊 Dungeon Statistics:');
    console.log(`   Total Objects: ${statsResult.result.stats.total_objects}`);
    console.log(`   Rooms: ${statsResult.result.stats.rooms}`);
    console.log(`   Walls: ${statsResult.result.stats.walls || 'N/A'}`);
    console.log(`   Lights: ${statsResult.result.stats.lights || 'N/A'}`);
    console.log(`   Decorations: ${statsResult.result.stats.decorations || 0}`);
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // STEP 5: Add Animation (Flickering Torches)
    // ═══════════════════════════════════════════════════════════════════
    console.log('STEP 5: Animate Flickering Torches');
    console.log('─'.repeat(70));
    console.log('🔥 Adding torch animations...');
    
    const animResult = await client.sendCommand('AnimateDungeon', {
      intensity: 0.3,  // Flicker intensity (0.0 - 1.0)
      speed: 1.0,      // Animation speed
      duration: 120,   // Frame duration
    });
    
    console.log('✅ Torches animated!');
    console.log(`   Lights Animated: ${animResult.result.lights_animated.length}`);
    console.log(`   Duration: ${animResult.result.duration} frames`);
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // STEP 6: Summary
    // ═══════════════════════════════════════════════════════════════════
    console.log('═'.repeat(70));
    console.log('✨ DUNGEON GENERATION COMPLETE!');
    console.log('═'.repeat(70));
    console.log('');
    console.log('📊 Final Summary:');
    console.log(`   Dungeon Name: ${dungeonResult.result.dungeon_name}`);
    console.log(`   Total Build Time: ${buildTime}ms`);
    console.log(`   Objects Created: ${dungeonResult.result.objects_created.length}`);
    console.log(`   Rooms: ${dungeonResult.result.rooms_created}`);
    console.log(`   Animated Lights: ${animResult.result.lights_animated.length}`);
    console.log('');
    console.log('🎮 What to do next:');
    console.log('   1. Open Blender to see your dungeon');
    console.log('   2. Press SPACEBAR to play the torch animation');
    console.log('   3. Use mouse to navigate the 3D viewport');
    console.log('   4. Modify this script to customize your dungeon!');
    console.log('');
    console.log('💡 Try changing:');
    console.log('   - dungeonConfig.size (grid size)');
    console.log('   - dungeonConfig.rooms (number of rooms)');
    console.log('   - dungeonConfig.style (medieval, sci-fi, fantasy)');
    console.log('   - Animation parameters (intensity, speed, duration)');
    console.log('');
    console.log('📚 Learn more: See ../DUNGEON_GENERATION_LEARNING.md');
    console.log('');

    // ═══════════════════════════════════════════════════════════════════
    // (Future) STEP 7: Export for Game Engine
    // ═══════════════════════════════════════════════════════════════════
    console.log('(Future Features - Coming Soon!)');
    console.log('─'.repeat(70));
    console.log('⏳ Export to GLB format');
    console.log('⏳ Generate navmesh for pathfinding');
    console.log('⏳ Export collision meshes');
    console.log('⏳ Create spawn points JSON');
    console.log('⏳ Package for Unity/Unreal/Godot');
    console.log('');

  } catch (error) {
    console.error('');
    console.error('❌ ERROR:', error.message);
    console.error('');
    console.error('Troubleshooting:');
    console.error('  1. Is Redis running? (redis-server)');
    console.error('  2. Is Blender running with sidecar?');
    console.error('  3. Check Redis connection in Blender console');
    console.error('');
    process.exit(1);
  } finally {
    await client.close();
  }
}

main();

