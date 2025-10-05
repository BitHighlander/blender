/**
 * MCP Socket Client for Blender
 * 
 * Connects to Blender's MCP server via TCP socket (port 9876)
 */

import { createConnection } from 'net';
import { EventEmitter } from 'events';

export class MCPClient extends EventEmitter {
  constructor(host = 'localhost', port = 9876) {
    super();
    this.host = host;
    this.port = port;
    this.socket = null;
    this.connected = false;
    this.pendingCommands = new Map();
  }

  /**
   * Connect to Blender MCP server
   */
  async connect() {
    return new Promise((resolve, reject) => {
      this.socket = createConnection({ host: this.host, port: this.port });

      this.socket.on('connect', () => {
        console.log(`✅ Connected to Blender MCP (${this.host}:${this.port})`);
        this.connected = true;
        resolve();
      });

      this.socket.on('data', (data) => {
        this._handleResponse(data);
      });

      this.socket.on('error', (err) => {
        console.error('❌ MCP socket error:', err.message);
        this.connected = false;
        reject(err);
      });

      this.socket.on('close', () => {
        console.log('🔌 Disconnected from Blender MCP');
        this.connected = false;
      });

      // Timeout after 5 seconds
      setTimeout(() => {
        if (!this.connected) {
          reject(new Error('Connection timeout'));
        }
      }, 5000);
    });
  }

  /**
   * Send a command to Blender
   * @param {string} type - Command type (e.g., 'ping', 'create_cube')
   * @param {object} params - Command parameters
   * @param {number} timeout - Timeout in ms (default 10000)
   * @returns {Promise<object>} Command result
   */
  async sendCommand(type, params = {}, timeout = 10000) {
    if (!this.connected) {
      throw new Error('Not connected to Blender MCP');
    }

    const commandId = Date.now() + Math.random();
    const command = { type, params };

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.pendingCommands.delete(commandId);
        reject(new Error(`Command timeout after ${timeout}ms`));
      }, timeout);

      this.pendingCommands.set(commandId, {
        resolve: (result) => {
          clearTimeout(timeoutId);
          resolve(result);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          reject(error);
        },
      });

      // Send command
      const data = JSON.stringify(command);
      this.socket.write(data);
      console.log(`[MCPClient] Sent: ${type}`);
    });
  }

  /**
   * Handle response from Blender
   * @private
   */
  _handleResponse(data) {
    try {
      const response = JSON.parse(data.toString());
      console.log(`[MCPClient] Received: ${response.status}`);

      // Match response to pending command (just take the first one for simplicity)
      const [commandId, pending] = this.pendingCommands.entries().next().value || [];
      
      if (pending) {
        this.pendingCommands.delete(commandId);
        
        if (response.status === 'success') {
          pending.resolve(response);
        } else {
          pending.reject(new Error(response.message || 'Command failed'));
        }
      }
    } catch (e) {
      console.error('Error parsing response:', e);
    }
  }

  /**
   * Convenience methods for common commands
   */

  async ping() {
    return this.sendCommand('ping', {});
  }

  async getSceneInfo() {
    return this.sendCommand('get_scene_info', {});
  }

  async createCube(options = {}) {
    return this.sendCommand('create_cube', {
      location: options.location || [0, 0, 0],
      size: options.size || 2,
    });
  }

  /**
   * Close connection
   */
  async close() {
    if (this.socket) {
      this.socket.end();
      this.connected = false;
    }
  }
}

