#!/usr/bin/env node
/**
 * Dungeon Builder Test - Degenerate Labs Blender
 * 
 * Tests the real-time sidecar with dungeon building!
 */

import { createClient } from 'redis';
import { randomUUID } from 'crypto';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const CMD_STREAM = 'blender:cmd';
const REPLY_STREAM = 'blender:reply:test';

// Create Redis client
const redis = createClient({ url: REDIS_URL });

redis.on('error', (err) => console.error('❌ Redis error:', err));

async function sendCommand(cmd, params = {}, opts = {}) {
  const trace_id = randomUUID();
  const span_id = randomUUID();
  
  const envelope = {
    cmd,
    params,
    opts: {
      ...opts,
      reply_stream: REPLY_STREAM,
    },
    trace_id,
    span_id,
  };
  
  console.log(`\n📤 Sending: ${cmd}`, params);
  
  // Send command
  await redis.xAdd(CMD_STREAM, '*', {
    payload: JSON.stringify(envelope),
  });
  
  // Wait for response
  const startTime = Date.now();
  const timeout = 30000; // 30 seconds
  
  while (Date.now() - startTime < timeout) {
    const messages = await redis.xRead(
      { key: REPLY_STREAM, id: '0' },
      { COUNT: 100 }
    );
    
    if (messages && messages.length > 0) {
      for (const msg of messages[0].messages) {
        const response = JSON.parse(msg.message.payload);
        
        if (response.trace_id === trace_id) {
          const elapsed = Date.now() - startTime;
          
          if (response.status === 'ok') {
            console.log(`✅ Success (${elapsed}ms):`, response.result);
            return response.result;
          } else {
            console.error(`❌ Error (${elapsed}ms):`, response.error);
            throw new Error(response.error.message);
          }
        }
      }
    }
    
    // Short delay before polling again
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  throw new Error(`⏰ Timeout waiting for response to ${cmd}`);
}

async function main() {
  try {
    console.log('🚀 Degenerate Labs Blender - Dungeon Builder Test\n');
    console.log('Connecting to Redis...');
    
    await redis.connect();
    console.log('✅ Connected to Redis\n');
    
    // 1. Check version
    console.log('═'.repeat(60));
    console.log('STEP 1: Verify Sidecar Version');
    console.log('═'.repeat(60));
    
    const pingResult = await sendCommand('Ping', { echo: 'version check' });
    
    console.log(`\n📊 Sidecar Info:`);
    console.log(`   Version: ${pingResult.sidecar_version} ✨`);
    console.log(`   Worker:  ${pingResult.worker_id}`);
    console.log(`   Blender: ${pingResult.blender_version}`);
    console.log(`   Build:   ${pingResult.blender_build}`);
    
    if (pingResult.sidecar_version !== '2.0.0-realtime') {
      console.warn(`\n⚠️  Expected version 2.0.0-realtime, got ${pingResult.sidecar_version}`);
    } else {
      console.log(`\n✅ Correct version: 2.0.0-realtime (with bpy.app.timers!)`);
    }
    
    // 2. Build the dungeon!
    console.log('\n' + '═'.repeat(60));
    console.log('STEP 2: BUILD THE DUNGEON! 🏰');
    console.log('═'.repeat(60));
    
    const dungeonParams = {
      size: 12,
      rooms: 7,
      style: 'medieval',  // 'medieval', 'sci-fi', or 'fantasy'
      add_lights: true,
      add_player: true,
    };
    
    console.log('\n🔨 Building dungeon with parameters:');
    console.log(JSON.stringify(dungeonParams, null, 2));
    
    const dungeonResult = await sendCommand('CreateDungeon', dungeonParams);
    
    console.log(`\n${dungeonResult.message}`);
    console.log(`   Dungeon Name: ${dungeonResult.dungeon_name}`);
    console.log(`   Rooms: ${dungeonResult.rooms_created}`);
    console.log(`   Objects: ${dungeonResult.objects_created.length}`);
    console.log(`   Build Time: ${dungeonResult.time_taken}s`);
    
    // 3. Get dungeon stats
    console.log('\n' + '═'.repeat(60));
    console.log('STEP 3: Dungeon Statistics');
    console.log('═'.repeat(60));
    
    const statsResult = await sendCommand('GetDungeonStats', {});
    
    console.log(`\n${statsResult.message}`);
    console.log(`   Stats:`, statsResult.stats);
    
    // 4. Animate the torches!
    console.log('\n' + '═'.repeat(60));
    console.log('STEP 4: Animate Flickering Torches 🔥');
    console.log('═'.repeat(60));
    
    const animResult = await sendCommand('AnimateDungeon', {
      intensity: 0.3,
      speed: 1.0,
      duration: 120,
    });
    
    console.log(`\n${animResult.message}`);
    console.log(`   Lights animated: ${animResult.lights_animated.join(', ')}`);
    console.log(`   Duration: ${animResult.duration} frames`);
    
    // Success!
    console.log('\n' + '═'.repeat(60));
    console.log('✨ SUCCESS! Dungeon Built and Animated!');
    console.log('═'.repeat(60));
    console.log('\n💡 The viewport should be updating in REAL-TIME!');
    console.log('   This proves bpy.app.timers is working correctly.\n');
    console.log('🎮 Open Blender and explore your dungeon!');
    console.log(`   Run: open ../build_darwin/bin/Blender.app\n`);
    
  } catch (error) {
    console.error('\n💥 Error:', error.message);
    process.exit(1);
  } finally {
    await redis.quit();
  }
}

main();

