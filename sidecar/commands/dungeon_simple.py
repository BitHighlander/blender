"""
Simple Dungeon Builder - Just works!

Creates a dungeon WITHOUT complex collection management.
Focus: Get something on screen in real-time!
"""

import bpy
import random
import math
from typing import Dict, Any


def create_simple_dungeon(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a simple dungeon - no fancy collections, just works!
    
    Params:
        size: int - Dungeon size (default: 8)
        rooms: int - Number of rooms (default: 4)
    """
    import time
    start_time = time.time()
    
    size = params.get("size", 8)
    num_rooms = params.get("rooms", 4)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    objects = []
    
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=size * 2, location=(0, 0, 0))
    objects.append("Floor")
    
    # Create rooms
    for i in range(num_rooms):
        x = random.uniform(-size, size)
        y = random.uniform(-size, size)
        
        # Room floor
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y, 0.5)
        )
        obj = bpy.context.scene.objects[-1]
        obj.name = f"Room_{i}"
        obj.scale = (2, 2, 1)
        obj.color = (0.3, 0.25, 0.2, 1.0)
        objects.append(obj.name)
        
        # 4 walls
        for j, (wall_x, wall_y) in enumerate([(x+1, y), (x-1, y), (x, y+1), (x, y-1)]):
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(wall_x, wall_y, 1.5)
            )
            wall = bpy.context.scene.objects[-1]
            wall.name = f"Wall_{i}_{j}"
            wall.scale = (0.2, 2, 3)
            wall.color = (0.4, 0.3, 0.25, 1.0)
            objects.append(wall.name)
        
        # Add light
        bpy.ops.object.light_add(type='POINT', location=(x, y, 3))
        light = bpy.context.scene.objects[-1]
        light.name = f"Light_{i}"
        light.data.energy = 100
        light.data.color = (1.0, 0.7, 0.3)
        objects.append(light.name)
    
    # Add camera
    bpy.ops.object.camera_add(
        location=(size, size, size),
        rotation=(math.radians(55), 0, math.radians(45))
    )
    camera = bpy.context.scene.objects[-1]
    camera.name = "DungeonCamera"
    bpy.context.scene.camera = camera
    objects.append("DungeonCamera")
    
    elapsed = time.time() - start_time
    
    return {
        "status": "success",
        "rooms": num_rooms,
        "objects": len(objects),
        "time_seconds": round(elapsed, 3),
        "message": f"🏰 Built {num_rooms} rooms with {len(objects)} objects in {elapsed:.2f}s!"
    }

