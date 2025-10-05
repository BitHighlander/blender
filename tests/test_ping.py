#!/usr/bin/env python3
"""
Test script for Ping command.

Usage:
    python tests/test_ping.py

Requirements:
    pip install redis
"""

import redis
import json
import time
import uuid
import sys


def test_ping(redis_url: str = "redis://localhost:6379/0", echo_message: str = "Hello from test!"):
    """
    Send a Ping command to the sidecar and wait for response.
    
    Args:
        redis_url: Redis connection URL
        echo_message: Message to echo back
    """
    print("=" * 60)
    print("🧪 Blender Sidecar - Ping Test")
    print("=" * 60)
    print(f"Redis: {redis_url}")
    print(f"Echo: {echo_message}")
    print()
    
    # Connect to Redis
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        print("\nMake sure Redis is running:")
        print("  docker run -d -p 6379:6379 redis:7-alpine")
        sys.exit(1)
    
    # Generate trace ID
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    
    # Build request
    request = {
        "v": "1.0",
        "cmd": "Ping",
        "params": {"echo": echo_message},
        "trace_id": trace_id,
        "span_id": span_id,
        "opts": {
            "reply_stream": "blender:reply",
        }
    }
    
    print(f"\n📤 Sending Ping command...")
    print(f"   Trace ID: {trace_id}")
    
    # Send command
    try:
        msg_id = r.xadd("blender:cmd", {"payload": json.dumps(request)})
        print(f"   Message ID: {msg_id}")
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        sys.exit(1)
    
    # Wait for response
    print(f"\n⏳ Waiting for response (timeout: 10s)...")
    
    start_time = time.time()
    timeout = 10
    
    while time.time() - start_time < timeout:
        try:
            # Read from reply stream
            messages = r.xread({"blender:reply": "0"}, count=100)
            
            for stream, message_list in messages:
                for msg_id, msg_data in message_list:
                    payload = json.loads(msg_data["payload"])
                    
                    # Check if this is our response
                    if payload.get("trace_id") == trace_id:
                        print("\n" + "=" * 60)
                        print("✅ Response received!")
                        print("=" * 60)
                        print()
                        
                        # Pretty print response
                        print("📥 Response:")
                        print(json.dumps(payload, indent=2))
                        print()
                        
                        # Extract key info
                        status = payload.get("status", "unknown")
                        result = payload.get("result", {})
                        error = payload.get("error")
                        metrics = payload.get("metrics", {})
                        
                        print("📊 Summary:")
                        print(f"   Status: {status}")
                        
                        if status == "ok":
                            print(f"   Echo: {result.get('echo', 'N/A')}")
                            print(f"   Blender: {result.get('blender_version', 'N/A')}")
                            print(f"   Sidecar: {result.get('sidecar_version', 'N/A')}")
                            print(f"   Worker: {result.get('worker_id', 'N/A')}")
                        elif status == "error":
                            print(f"   Error Code: {error.get('code', 'N/A')}")
                            print(f"   Error Message: {error.get('message', 'N/A')}")
                        
                        print(f"\n⏱️  Metrics:")
                        print(f"   CPU Time: {metrics.get('cpu_ms', 0)} ms")
                        print(f"   Wall Time: {metrics.get('wall_ms', 0)} ms")
                        print(f"   Memory: {metrics.get('mem_mb', 0)} MB")
                        print()
                        print("=" * 60)
                        
                        return payload
            
            # Not found yet, wait a bit
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error reading response: {e}")
            sys.exit(1)
    
    # Timeout
    print(f"\n❌ Timeout: No response received after {timeout}s")
    print("\nMake sure the sidecar is running:")
    print("  blender -b --python sidecar.py")
    sys.exit(1)


if __name__ == "__main__":
    # Parse command line args (optional)
    redis_url = sys.argv[1] if len(sys.argv) > 1 else "redis://localhost:6379/0"
    echo_msg = sys.argv[2] if len(sys.argv) > 2 else "Hello from test script!"
    
    test_ping(redis_url, echo_msg)

