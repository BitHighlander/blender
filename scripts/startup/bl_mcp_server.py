"""
Blender MCP Socket Server - First-Class Integration
Auto-starts when Blender launches. No addon needed.

Runs a socket server on port 9876 for MCP clients to connect.
Uses threading + bpy.app.timers for safe, non-blocking execution.
"""

import bpy
import json
import threading
import socket
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlenderMCP")

# Server instance (global)
_mcp_server = None


class BlenderMCPServer:
    """Socket server for MCP integration - runs in background thread."""
    
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
        logger.info(f"🎯 Initializing Blender MCP Server on {host}:{port}")

    def start(self):
        """Start the MCP socket server in a background thread."""
        if self.running:
            logger.warning("MCP Server already running")
            return

        self.running = True

        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)

            # Start server thread (daemon = won't block Blender exit)
            self.server_thread = threading.Thread(
                target=self._server_loop,
                name="BlenderMCP",
                daemon=True
            )
            self.server_thread.start()

            logger.info(f"✅ Blender MCP Server started on {self.host}:{self.port}")
            logger.info(f"   FastMCP clients can now connect!")
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            self.stop()

    def stop(self):
        """Stop the MCP server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        logger.info("🛑 MCP Server stopped")

    def _server_loop(self):
        """Main server loop - runs in background thread."""
        logger.info("MCP Server thread started")
        self.socket.settimeout(1.0)

        while self.running:
            try:
                try:
                    client, address = self.socket.accept()
                    logger.info(f"📥 MCP client connected: {address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue  # Just check running condition
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in server loop: {e}")
                    
        logger.info("MCP Server thread stopped")

    def _handle_client(self, client):
        """Handle a connected MCP client."""
        client.settimeout(None)
        buffer = b''

        try:
            while self.running:
                data = client.recv(8192)
                if not data:
                    logger.info("Client disconnected")
                    break

                buffer += data
                try:
                    command = json.loads(buffer.decode('utf-8'))
                    buffer = b''

                    # Execute command in Blender's main thread via bpy.app.timers
                    def execute_wrapper():
                        try:
                            response = self.execute_command(command)
                            response_json = json.dumps(response)
                            try:
                                client.sendall(response_json.encode('utf-8'))
                            except:
                                logger.warning("Client disconnected before response sent")
                        except Exception as e:
                            logger.error(f"Command execution error: {e}")
                            traceback.print_exc()
                        return None  # Don't repeat timer

                    # THE KEY: Queue execution in main thread
                    bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    
                except json.JSONDecodeError:
                    pass  # Incomplete data, wait for more
                    
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            try:
                client.close()
            except:
                pass

    def execute_command(self, command):
        """Execute a command in Blender's main thread."""
        cmd_type = command.get("type")
        params = command.get("params", {})

        try:
            # Simple command handlers
            if cmd_type == "get_scene_info":
                return {
                    "status": "success",
                    "result": {
                        "objects": len(bpy.data.objects),
                        "meshes": len(bpy.data.meshes),
                        "lights": len(bpy.data.lights),
                        "cameras": len(bpy.data.cameras),
                    }
                }
            
            elif cmd_type == "create_cube":
                location = params.get("location", [0, 0, 0])
                size = params.get("size", 2)
                
                bpy.ops.mesh.primitive_cube_add(size=size, location=location)
                obj = bpy.context.view_layer.objects.active or bpy.context.scene.objects[-1]
                
                return {
                    "status": "success",
                    "result": {
                        "name": obj.name,
                        "location": list(obj.location),
                        "message": f"Created cube '{obj.name}' at {location}"
                    }
                }
            
            elif cmd_type == "ping":
                return {
                    "status": "success",
                    "result": {
                        "pong": True,
                        "blender_version": bpy.app.version_string,
                        "message": "Blender MCP Server is alive!"
                    }
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {cmd_type}"
                }
                
        except Exception as e:
            logger.error(f"Command error: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": str(e)
            }


def start_mcp_server():
    """Auto-start the MCP server when Blender loads."""
    global _mcp_server
    
    if _mcp_server is None:
        _mcp_server = BlenderMCPServer(host='localhost', port=9876)
        _mcp_server.start()
    
    return None  # Don't repeat timer


# Auto-start the MCP server 2 seconds after Blender loads
def register():
    """Called by Blender on startup."""
    bpy.app.timers.register(start_mcp_server, first_interval=2.0)
    logger.info("🚀 Blender MCP Server will start in 2 seconds...")


def unregister():
    """Called by Blender on shutdown."""
    global _mcp_server
    if _mcp_server:
        _mcp_server.stop()


# Auto-register (this script is in startup/)
if __name__ != "__main__":
    register()

