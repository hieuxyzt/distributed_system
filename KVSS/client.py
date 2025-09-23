#!/usr/bin/env python3
"""
Mini Key-Value Store Service (KVSS) Client
Connects to KVSS server and provides command-line interface
"""

import socket
import sys
from datetime import datetime
import os


class KVSSClient:
    def __init__(self, host='127.0.0.1', port=5050, log_file=None):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.log_file = log_file or f"kvss_client_{host}_{port}.log"
        
    def log_message(self, message):
        """Write log message to both console and file"""
        print(message)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Warning: Could not write to log file {self.log_file}: {e}")
    
    def connect(self):
        """Connect to the KVSS server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_message(f"[{timestamp}] [CONNECT] Connected to KVSS server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the KVSS server"""
        if self.socket:
            self.socket.close()
            self.connected = False
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_message(f"[{timestamp}] [DISCONNECT] Disconnected from server")
    
    def send_command(self, command):
        """Send a command to the server and return the response"""
        if not self.connected:
            return "Error: Not connected to server"
        
        try:
            # Send command as-is (user must include KV/1.0 prefix)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_message(f"[{timestamp}] [SEND] to {self.host}:{self.port}: {command}")
            self.socket.send(f"{command}\n".encode('utf-8'))
            
            # Receive response
            response = self.socket.recv(1024).decode('utf-8').strip()
            self.log_message(f"[{timestamp}] [RECV] from {self.host}:{self.port}: {response}")
            return response
            
        except Exception as e:
            print(f"Error sending command: {e}")
            self.connected = False
            return "Error: Connection lost"
    
    def interactive_mode(self):
        """Run in interactive mode with command prompt"""
        print("KVSS Client - Interactive Mode")
        print("Commands: KV/1.0 PUT <key> <value>, KV/1.0 GET <key>, KV/1.0 DEL <key>, KV/1.0 STATS, KV/1.0 QUIT")
        print("Type 'help' for more information or 'exit' to quit")
        print("Note: All server commands MUST start with 'KV/1.0' prefix!")
        print()
        
        while True:
            try:
                command = input("KVSS> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    # Send QUIT to server first with proper protocol
                    if self.connected:
                        response = self.send_command("KV/1.0 QUIT")
                    break
                elif command.lower() == 'help':
                    self.print_help()
                    continue
                elif command.lower() == 'connect':
                    if not self.connected:
                        self.connect()
                    else:
                        print("Already connected")
                    continue
                elif command.lower() == 'disconnect':
                    self.disconnect()
                    continue
                elif command == '':
                    continue
                
                if not self.connected:
                    print("Not connected to server. Type 'connect' to connect.")
                    continue
                
                response = self.send_command(command)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nExiting...")
                break
    
    def batch_mode(self, commands):
        """Execute a list of commands in batch mode"""
        results = []
        for command in commands:
            response = self.send_command(command)
            results.append(f"{command} -> {response}")
            print(f"{command} -> {response}")
        return results
    
    def print_help(self):
        """Print help information"""
        help_text = """
KVSS Client Commands (must include KV/1.0 prefix):
  KV/1.0 PUT <key> <value>  - Store a key-value pair
  KV/1.0 GET <key>          - Retrieve value for a key
  KV/1.0 DEL <key>          - Delete a key-value pair
  KV/1.0 STATS              - Show server statistics
  KV/1.0 QUIT               - Disconnect from server (server remains running)
  
Client Commands:
  help               - Show this help
  connect            - Connect to server
  disconnect         - Disconnect from server
  exit               - Exit client (automatically sends KV/1.0 QUIT)

Examples:
  KV/1.0 PUT mykey myvalue
  KV/1.0 GET mykey
  KV/1.0 DEL mykey
  KV/1.0 STATS

Note: All server commands MUST start with 'KV/1.0' prefix!
Logging: All client activities are logged to file: {self.log_file}
        """
        print(help_text)


def main():
    # Default values
    host = '127.0.0.1'
    port = 5050
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python client.py [host] [port] [command...]")
            print("  host: server hostname (default: 127.0.0.1)")
            print("  port: server port (default: 5050)")
            print("  command: optional command to execute (otherwise interactive mode)")
            print("\nExamples:")
            print("  python client.py")
            print("  python client.py 192.168.1.100 5050")
            print("  python client.py 127.0.0.1 5050 GET mykey")
            return
        host = sys.argv[1]
    
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number")
            sys.exit(1)
    
    # Create client
    client = KVSSClient(host, port)
    
    # Connect to server
    if not client.connect():
        sys.exit(1)
    
    try:
        # Check if command provided as argument
        if len(sys.argv) >= 4:
            # Batch mode - execute single command
            command = ' '.join(sys.argv[3:])
            response = client.send_command(command)
        else:
            # Interactive mode
            client.interactive_mode()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
