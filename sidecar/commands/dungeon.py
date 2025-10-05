"""
Dungeon Builder - Procedural dungeon generation for Blender

Demonstrates real-time, non-blocking command execution with bpy.app.timers!
"""

import bpy
import random
import math
from typing import Dict, Any, List, Tuple


def create_dungeon(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a procedural dungeon scene!
    
    Params:
        size: int - Dungeon grid size (default: 10)
        rooms: int - Number of rooms (default: 5)
        style: str - "medieval", "sci-fi", or "fantasy" (default: "medieval")
        add_lights: bool - Add torch lights (default: True)
        add_player: bool - Add a player spawn point (default: True)
    
    Returns:
        Dict with:
            - dungeon_name: str
            - rooms_created: int
            - objects_created: List[str]
            - time_taken: float
    """
    import time
    start_time = time.time()
    
    # Extract parameters
    grid_size = params.get("size", 10)
    num_rooms = params.get("rooms", 5)
    style = params.get("style", "medieval")
    add_lights = params.get("add_lights", True)
    add_player = params.get("add_player", True)
    
    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    objects_created = []
    dungeon_name = f"Dungeon_{style}_{int(time.time())}"
    
    # Create dungeon collection
    dungeon_collection = bpy.data.collections.new(dungeon_name)
    bpy.context.scene.collection.children.link(dungeon_collection)
    
    # 1. Create floor
    bpy.ops.mesh.primitive_plane_add(size=grid_size * 2, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Dungeon_Floor"
    
    # Link to dungeon collection
    bpy.context.scene.collection.objects.unlink(floor)
    dungeon_collection.objects.link(floor)
    objects_created.append(floor.name)
    
    # 2. Create rooms
    rooms = _generate_room_layout(grid_size, num_rooms)
    
    for i, (x, y, width, height) in enumerate(rooms):
        # Create room floor piece
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y, 0.5)
        )
        room = bpy.context.active_object
        room.name = f"Room_{i}"
        room.scale = (width, height, 1)
        
        # Link to collection
        bpy.context.scene.collection.objects.unlink(room)
        dungeon_collection.objects.link(room)
        objects_created.append(room.name)
        
        # Add walls around room
        wall_objs = _create_room_walls(x, y, width, height, dungeon_collection, style)
        objects_created.extend(wall_objs)
        
        # Add torch lights if requested
        if add_lights:
            light_objs = _add_room_lights(x, y, width, height, dungeon_collection)
            objects_created.extend(light_objs)
    
    # 3. Create corridors between rooms
    corridor_objs = _create_corridors(rooms, dungeon_collection)
    objects_created.extend(corridor_objs)
    
    # 4. Add decorative elements based on style
    if style == "medieval":
        deco_objs = _add_medieval_decorations(rooms, dungeon_collection)
        objects_created.extend(deco_objs)
    elif style == "sci-fi":
        deco_objs = _add_scifi_decorations(rooms, dungeon_collection)
        objects_created.extend(deco_objs)
    elif style == "fantasy":
        deco_objs = _add_fantasy_decorations(rooms, dungeon_collection)
        objects_created.extend(deco_objs)
    
    # 5. Add player spawn point
    if add_player:
        spawn_room = rooms[0]  # Spawn in first room
        bpy.ops.object.empty_add(
            type='SPHERE',
            location=(spawn_room[0], spawn_room[1], 2)
        )
        player_spawn = bpy.context.active_object
        player_spawn.name = "Player_Spawn"
        player_spawn.scale = (0.5, 0.5, 0.5)
        
        bpy.context.scene.collection.objects.unlink(player_spawn)
        dungeon_collection.objects.link(player_spawn)
        objects_created.append(player_spawn.name)
    
    # 6. Add a camera
    bpy.ops.object.camera_add(
        location=(grid_size, grid_size, grid_size * 1.5),
        rotation=(math.radians(55), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.name = "Dungeon_Camera"
    bpy.context.scene.camera = camera
    
    bpy.context.scene.collection.objects.unlink(camera)
    dungeon_collection.objects.link(camera)
    objects_created.append(camera.name)
    
    # 7. Set viewport shading
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.light = 'STUDIO'
    
    time_taken = time.time() - start_time
    
    return {
        "dungeon_name": dungeon_name,
        "rooms_created": len(rooms),
        "objects_created": objects_created,
        "time_taken": round(time_taken, 3),
        "message": f"🏰 Dungeon '{dungeon_name}' created with {len(rooms)} rooms and {len(objects_created)} objects in {time_taken:.2f}s!"
    }


def _generate_room_layout(grid_size: int, num_rooms: int) -> List[Tuple[float, float, float, float]]:
    """Generate room positions and sizes."""
    rooms = []
    occupied = set()
    
    for _ in range(num_rooms):
        # Random room size
        width = random.uniform(2, 4)
        height = random.uniform(2, 4)
        
        # Find unoccupied position
        for attempt in range(50):
            x = random.uniform(-grid_size + width, grid_size - width)
            y = random.uniform(-grid_size + height, grid_size - height)
            
            # Check if overlaps with existing rooms
            overlaps = False
            grid_x, grid_y = int(x), int(y)
            if (grid_x, grid_y) not in occupied:
                occupied.add((grid_x, grid_y))
                rooms.append((x, y, width, height))
                break
    
    return rooms


def _create_room_walls(
    x: float, 
    y: float, 
    width: float, 
    height: float,
    collection,
    style: str
) -> List[str]:
    """Create walls around a room."""
    walls = []
    wall_height = 3
    wall_thickness = 0.2
    
    # Define wall positions (N, S, E, W)
    wall_configs = [
        ("North", (x, y + height/2, wall_height/2), (width, wall_thickness, wall_height)),
        ("South", (x, y - height/2, wall_height/2), (width, wall_thickness, wall_height)),
        ("East", (x + width/2, y, wall_height/2), (wall_thickness, height, wall_height)),
        ("West", (x - width/2, y, wall_height/2), (wall_thickness, height, wall_height)),
    ]
    
    for wall_dir, location, scale in wall_configs:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        wall = bpy.context.active_object
        wall.name = f"Wall_{wall_dir}_{int(x)}_{int(y)}"
        wall.scale = scale
        
        # Style-specific materials
        if style == "medieval":
            wall.color = (0.3, 0.25, 0.2, 1.0)  # Stone brown
        elif style == "sci-fi":
            wall.color = (0.1, 0.15, 0.2, 1.0)  # Dark metal
        elif style == "fantasy":
            wall.color = (0.4, 0.3, 0.5, 1.0)  # Purple mystical
        
        bpy.context.scene.collection.objects.unlink(wall)
        collection.objects.link(wall)
        walls.append(wall.name)
    
    return walls


def _add_room_lights(
    x: float,
    y: float,
    width: float,
    height: float,
    collection
) -> List[str]:
    """Add torch/lights to room."""
    lights = []
    
    # Add 4 corner torches
    corners = [
        (x + width/3, y + height/3),
        (x - width/3, y + height/3),
        (x + width/3, y - height/3),
        (x - width/3, y - height/3),
    ]
    
    for i, (lx, ly) in enumerate(corners):
        bpy.ops.object.light_add(type='POINT', location=(lx, ly, 2))
        light = bpy.context.active_object
        light.name = f"Torch_{int(x)}_{int(y)}_{i}"
        light.data.energy = 50
        light.data.color = (1.0, 0.7, 0.3)  # Warm torch color
        
        bpy.context.scene.collection.objects.unlink(light)
        collection.objects.link(light)
        lights.append(light.name)
    
    return lights


def _create_corridors(rooms: List[Tuple[float, float, float, float]], collection) -> List[str]:
    """Create corridors connecting rooms."""
    corridors = []
    
    # Connect each room to the next
    for i in range(len(rooms) - 1):
        x1, y1, _, _ = rooms[i]
        x2, y2, _, _ = rooms[i + 1]
        
        # Midpoint for corridor
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Distance
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Angle
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Create corridor
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(mid_x, mid_y, 0.5)
        )
        corridor = bpy.context.active_object
        corridor.name = f"Corridor_{i}"
        corridor.scale = (distance / 2, 1, 1)
        corridor.rotation_euler = (0, 0, angle)
        corridor.color = (0.2, 0.2, 0.2, 1.0)
        
        bpy.context.scene.collection.objects.unlink(corridor)
        collection.objects.link(corridor)
        corridors.append(corridor.name)
    
    return corridors


def _add_medieval_decorations(rooms: List[Tuple[float, float, float, float]], collection) -> List[str]:
    """Add medieval-style decorations (pillars, etc)."""
    decorations = []
    
    for i, (x, y, width, height) in enumerate(rooms):
        if random.random() > 0.5:  # 50% chance
            # Add a pillar in center
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.3,
                depth=3,
                location=(x, y, 1.5)
            )
            pillar = bpy.context.active_object
            pillar.name = f"Pillar_{i}"
            pillar.color = (0.4, 0.35, 0.3, 1.0)
            
            bpy.context.scene.collection.objects.unlink(pillar)
            collection.objects.link(pillar)
            decorations.append(pillar.name)
    
    return decorations


def _add_scifi_decorations(rooms: List[Tuple[float, float, float, float]], collection) -> List[str]:
    """Add sci-fi style decorations (tech panels, etc)."""
    decorations = []
    
    for i, (x, y, width, height) in enumerate(rooms):
        if random.random() > 0.6:  # 40% chance
            # Add a tech panel
            bpy.ops.mesh.primitive_cube_add(
                size=0.1,
                location=(x + width/2 - 0.05, y, 2)
            )
            panel = bpy.context.active_object
            panel.name = f"TechPanel_{i}"
            panel.scale = (0.1, 1, 1)
            panel.color = (0.1, 0.3, 0.5, 1.0)  # Blue glow
            
            bpy.context.scene.collection.objects.unlink(panel)
            collection.objects.link(panel)
            decorations.append(panel.name)
    
    return decorations


def _add_fantasy_decorations(rooms: List[Tuple[float, float, float, float]], collection) -> List[str]:
    """Add fantasy-style decorations (crystals, etc)."""
    decorations = []
    
    for i, (x, y, width, height) in enumerate(rooms):
        if random.random() > 0.5:  # 50% chance
            # Add a magical crystal
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.3,
                location=(x + random.uniform(-width/3, width/3), 
                         y + random.uniform(-height/3, height/3), 
                         1)
            )
            crystal = bpy.context.active_object
            crystal.name = f"Crystal_{i}"
            crystal.scale = (0.5, 0.5, 1.5)  # Tall crystal
            crystal.color = (0.5, 0.2, 0.8, 1.0)  # Purple magic
            
            bpy.context.scene.collection.objects.unlink(crystal)
            collection.objects.link(crystal)
            decorations.append(crystal.name)
    
    return decorations


def animate_dungeon(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Animate torch lights flickering!
    
    Params:
        intensity: float - Flicker intensity (default: 0.2)
        speed: float - Animation speed (default: 1.0)
        duration: int - Animation length in frames (default: 120)
    
    Returns:
        Dict with animation info
    """
    intensity = params.get("intensity", 0.2)
    speed = params.get("speed", 1.0)
    duration = params.get("duration", 120)
    
    lights_animated = []
    
    # Find all torch lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and 'Torch' in obj.name:
            light = obj.data
            base_energy = light.energy
            
            # Keyframe flickering
            for frame in range(0, duration, 5):
                bpy.context.scene.frame_set(frame)
                
                # Random flicker
                flicker = random.uniform(-intensity, intensity)
                light.energy = base_energy * (1 + flicker)
                light.keyframe_insert(data_path="energy", frame=frame)
            
            lights_animated.append(obj.name)
    
    # Set animation range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = duration
    
    return {
        "lights_animated": lights_animated,
        "duration": duration,
        "message": f"🔥 Animated {len(lights_animated)} torches with flickering!"
    }


def get_dungeon_stats(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """Get statistics about the current dungeon."""
    
    stats = {
        "total_objects": len(bpy.data.objects),
        "rooms": 0,
        "walls": 0,
        "lights": 0,
        "corridors": 0,
        "decorations": 0,
        "collections": len(bpy.data.collections),
    }
    
    for obj in bpy.data.objects:
        if "Room_" in obj.name:
            stats["rooms"] += 1
        elif "Wall_" in obj.name:
            stats["walls"] += 1
        elif "Torch" in obj.name:
            stats["lights"] += 1
        elif "Corridor_" in obj.name:
            stats["corridors"] += 1
        elif any(dec in obj.name for dec in ["Pillar", "Crystal", "TechPanel"]):
            stats["decorations"] += 1
    
    return {
        "stats": stats,
        "message": f"📊 Dungeon stats: {stats['rooms']} rooms, {stats['walls']} walls, {stats['lights']} lights"
    }

