"""
Redis Streams consumer for the sidecar.

Consumes commands from Redis Streams, routes them, and sends responses.
"""

import json
import logging
import time
import uuid
import traceback
from typing import Dict, Any, Optional

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None

from .router import CommandRouter
from .errors import SidecarError
from .telemetry import Metrics, create_response


class RedisConsumer:
    """Consumes commands from Redis Streams."""
    
    def __init__(self, config: Dict[str, Any], router: CommandRouter):
        self.config = config
        self.router = router
        self.logger = logging.getLogger("sidecar")
        
        if not HAS_REDIS:
            raise RuntimeError("redis-py not installed. Install with: pip install redis")
        
        # Initialize Redis connection
        redis_url = config["redis"]["url"]
        self.logger.info(f"Connecting to Redis: {redis_url}")
        
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.logger.info("✅ Redis connection established")
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
        
        self.cmd_stream = config["redis"]["cmd_stream"]
        self.reply_stream = config["redis"]["reply_stream_default"]
        self.consumer_group = config["redis"]["consumer_group"]
        self.consumer_name = config["redis"]["consumer_name"]
        
        self.running = False
        
        # Ensure consumer group exists
        self._ensure_consumer_group()
    
    def _ensure_consumer_group(self) -> None:
        """Ensure the consumer group exists."""
        try:
            # Try to create the consumer group
            self.redis_client.xgroup_create(
                name=self.cmd_stream,
                groupname=self.consumer_group,
                id="0",
                mkstream=True,
            )
            self.logger.info(f"Created consumer group: {self.consumer_group}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                # Group already exists
                self.logger.debug(f"Consumer group already exists: {self.consumer_group}")
            else:
                raise
    
    def run(self) -> None:
        """Main consumer loop."""
        self.running = True
        self.logger.info(f"👂 Listening for commands on {self.cmd_stream}...")
        
        while self.running:
            try:
                # Read from stream (blocking with timeout)
                messages = self.redis_client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.cmd_stream: ">"},
                    count=1,
                    block=5000,  # 5 second timeout
                )
                
                if not messages:
                    # No messages, continue
                    continue
                
                # Process each message
                for stream_name, message_list in messages:
                    for message_id, message_data in message_list:
                        self._process_message(message_id, message_data)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt, stopping...")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Error in consumer loop: {e}", exc_info=True)
                time.sleep(1)  # Back off on error
    
    def _process_message(self, message_id: str, message_data: Dict[str, str]) -> None:
        """Process a single message from the stream."""
        try:
            # Parse payload
            payload_str = message_data.get("payload", "{}")
            request = json.loads(payload_str)
            
            self.logger.debug(f"Received message {message_id}: {request.get('cmd', 'UNKNOWN')}")
            
            # Extract envelope fields
            cmd = request.get("cmd", "")
            params = request.get("params", {})
            opts = request.get("opts", {})
            trace_id = request.get("trace_id", str(uuid.uuid4()))
            span_id = request.get("span_id", str(uuid.uuid4()))
            
            # Start metrics
            metrics_collector = Metrics()
            
            # Route command
            try:
                result = self.router.route(cmd, params, opts)
                
                # Collect metrics
                metrics = metrics_collector.collect()
                
                # Create success response
                response = create_response(
                    trace_id=trace_id,
                    span_id=span_id,
                    cmd=cmd,
                    status="ok",
                    result=result,
                    metrics=metrics,
                )
                
                self.logger.info(f"✅ Command succeeded: {cmd} (trace={trace_id})")
                
            except SidecarError as e:
                # Collect metrics
                metrics = metrics_collector.collect()
                
                # Create error response
                response = create_response(
                    trace_id=trace_id,
                    span_id=span_id,
                    cmd=cmd,
                    status="error",
                    error=e.to_dict(),
                    metrics=metrics,
                )
                
                self.logger.error(f"❌ Command failed: {cmd} ({e.code}): {e.message}")
            
            except Exception as e:
                # Unexpected error
                metrics = metrics_collector.collect()
                
                response = create_response(
                    trace_id=trace_id,
                    span_id=span_id,
                    cmd=cmd,
                    status="error",
                    error={
                        "code": "E_INTERNAL",
                        "message": str(e),
                        "details": {"traceback": traceback.format_exc()},
                        "retryable": True,
                    },
                    metrics=metrics,
                )
                
                self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            
            # Send response
            reply_stream = opts.get("reply_stream", self.reply_stream)
            self._send_response(reply_stream, response)
            
            # Acknowledge message
            self.redis_client.xack(self.cmd_stream, self.consumer_group, message_id)
            self.logger.debug(f"Acknowledged message: {message_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to process message {message_id}: {e}", exc_info=True)
            # Note: Message will be re-delivered if not acked
    
    def _send_response(self, stream: str, response: Dict[str, Any]) -> None:
        """Send response to Redis stream."""
        try:
            response_json = json.dumps(response)
            self.redis_client.xadd(
                name=stream,
                fields={"payload": response_json},
            )
            self.logger.debug(f"Sent response to {stream}")
        except Exception as e:
            self.logger.error(f"Failed to send response: {e}", exc_info=True)
    
    def shutdown(self) -> None:
        """Shutdown the consumer gracefully."""
        self.logger.info("Shutting down consumer...")
        self.running = False
        
        # Wait for consumer thread to finish
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.logger.info("Waiting for consumer thread to stop...")
            self.consumer_thread.join(timeout=5.0)
            if self.consumer_thread.is_alive():
                self.logger.warning("Consumer thread did not stop gracefully")
        
        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
            self.logger.info("Redis connection closed")
    
    def wait_forever(self) -> None:
        """Block main thread while consumer runs in background.
        
        This keeps Blender running and responsive. The consumer thread
        handles Redis messages and queues them via bpy.app.timers.
        """
        self.logger.info("Main thread waiting (consumer runs in background)...")
        try:
            while self.running and self.consumer_thread and self.consumer_thread.is_alive():
                time.sleep(0.1)  # Short sleep, Blender stays responsive
        except KeyboardInterrupt:
            self.logger.info("Interrupt received")
            self.shutdown()

