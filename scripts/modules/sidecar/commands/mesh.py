"""
Mesh creation command handlers.

Basic mesh primitives for building geometry.
"""

import bpy
from typing import Dict, Any


def handle_create_cube(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle CreateCube command.
    
    Args:
        config: Sidecar configuration
        params: Command parameters
            - name: Object name
            - location: [x, y, z] position
            - size: Cube size
        opts: Command options
    
    Returns:
        Result dictionary with object info
    """
    name = params.get("name", "Cube")
    location = params.get("location", [0, 0, 0])
    size = params.get("size", 2.0)
    
    # Create mesh data
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    
    # Link to scene
    bpy.context.scene.collection.objects.link(obj)
    
    # Force viewport update
    bpy.context.view_layer.update()
    
    # Trigger redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
    return {
        "object_name": obj.name,
        "location": list(obj.location),
        "size": size,
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
    }


def handle_get_scene_info(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle GetSceneInfo command.
    
    Returns information about the current Blender scene.
    Matches the MCP 'get_scene_info' command.
    
    Args:
        config: Sidecar configuration
        params: Command parameters (none required)
        opts: Command options
    
    Returns:
        Result dictionary with scene statistics
    """
    return {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "lights": len(bpy.data.lights),
        "cameras": len(bpy.data.cameras),
    }


def handle_create_room(config: Dict[str, Any], params: Dict[str, Any], opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle CreateRoom command.
    
    Creates a simple rectangular room (floor + 4 walls + ceiling).
    
    Args:
        config: Sidecar configuration
        params: Command parameters
            - name: Room name
            - location: [x, y, z] position
            - width: Room width (X axis)
            - depth: Room depth (Y axis)
            - height: Room height (Z axis)
        opts: Command options
    
    Returns:
        Result dictionary with room info
    """
    name = params.get("name", "Room")
    location = params.get("location", [0, 0, 0])
    width = params.get("width", 10.0)
    depth = params.get("depth", 10.0)
    height = params.get("height", 3.0)
    
    import bmesh
    
    x, y, z = location
    created_objects = []
    
    # Create collection for this room
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    # Helper function to create a scaled cube
    def create_box(obj_name, loc, scale):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        mesh = bpy.data.meshes.new(f"{obj_name}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new(obj_name, mesh)
        obj.location = loc
        obj.scale = scale
        collection.objects.link(obj)
        return obj
    
    # Wall thickness
    wall_thickness = 0.5
    
    # Floor
    floor = create_box(
        f"{name}_Floor",
        (x, y, z - 0.5),
        (width, depth, 1.0)
    )
    created_objects.append(floor.name)
    
    # Ceiling
    ceiling = create_box(
        f"{name}_Ceiling",
        (x, y, z + height - 0.5),
        (width, depth, 1.0)
    )
    created_objects.append(ceiling.name)
    
    # Wall North (+Y)
    wall_n = create_box(
        f"{name}_Wall_N",
        (x, y + depth/2 - wall_thickness/2, z + height/2 - 0.5),
        (width, wall_thickness, height - 1)
    )
    created_objects.append(wall_n.name)
    
    # Wall South (-Y)
    wall_s = create_box(
        f"{name}_Wall_S",
        (x, y - depth/2 + wall_thickness/2, z + height/2 - 0.5),
        (width, wall_thickness, height - 1)
    )
    created_objects.append(wall_s.name)
    
    # Wall East (+X)
    wall_e = create_box(
        f"{name}_Wall_E",
        (x + width/2 - wall_thickness/2, y, z + height/2 - 0.5),
        (wall_thickness, depth, height - 1)
    )
    created_objects.append(wall_e.name)
    
    # Wall West (-X)
    wall_w = create_box(
        f"{name}_Wall_W",
        (x - width/2 + wall_thickness/2, y, z + height/2 - 0.5),
        (wall_thickness, depth, height - 1)
    )
    created_objects.append(wall_w.name)
    
    # Force viewport update
    bpy.context.view_layer.update()
    
    # Trigger redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
    return {
        "room_name": name,
        "collection": collection.name,
        "location": location,
        "dimensions": {
            "width": width,
            "depth": depth,
            "height": height,
        },
        "objects": created_objects,
        "object_count": len(created_objects),
    }

