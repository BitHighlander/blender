#!/usr/bin/env python3
"""
Simple test to verify Blender MCP socket server is working
"""

import socket
import json
import time

HOST = 'localhost'
PORT = 9876

def test_socket_connection():
    """Test basic socket connection to Blender MCP addon"""
    print("🔌 Testing connection to Blender MCP addon...")
    print(f"   Host: {HOST}")
    print(f"   Port: {PORT}")
    print("")
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        # Connect
        sock.connect((HOST, PORT))
        print("✅ Connected to Blender MCP addon!")
        print("")
        
        # Send a simple command
        command = {
            "type": "get_scene_info",
            "params": {}
        }
        
        print(f"📤 Sending command: {command['type']}")
        sock.sendall(json.dumps(command).encode('utf-8'))
        
        # Receive response
        response_data = sock.recv(8192)
        response = json.loads(response_data.decode('utf-8'))
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        print("")
        
        if response.get("status") == "success":
            print("✅ MCP addon is working!")
            return True
        else:
            print(f"⚠️  Response status: {response.get('status')}")
            return False
            
    except ConnectionRefusedError:
        print("❌ Connection refused - Blender MCP addon not running")
        print("   Make sure Blender is open with the addon enabled")
        return False
    except socket.timeout:
        print("⏰ Timeout - addon might be starting up")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    success = test_socket_connection()
    exit(0 if success else 1)

