#!/usr/bin/env python3
"""
Mini Key-Value Store Service (KVSS) Server
Implements a TCP-based key-value store with text-based protocol
"""

import socket
import threading
import sys
import time
from datetime import datetime
import os


class KVSSServer:
    def __init__(self, host='127.0.0.1', port=5050, log_file=None):
        self.host = host
        self.port = port
        self.data_store = {}  # In-memory key-value store
        self.server_socket = None
        self.running = False
        self.print_lock = threading.Lock()  # Lock for thread-safe printing
        self.log_file = log_file or f"kvss_server_{host}_{port}.log"
        self.stats = {
            'start_time': None,
            'connections': 0,
            'commands_processed': 0,
            'get_requests': 0,
            'put_requests': 0,
            'del_requests': 0
        }
    
    def safe_print(self, message):
        """Thread-safe printing with immediate flush"""
        with self.print_lock:
            print(message, flush=True)
    
    def safe_log(self, message):
        """Thread-safe logging to both console and file"""
        with self.print_lock:
            print(message, flush=True)
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{message}\n")
            except Exception as e:
                print(f"Warning: Could not write to log file {self.log_file}: {e}", flush=True)
    
    def start(self):
        """Start the KVSS server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # Set timeout to make it interruptible
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            self.safe_log(f"KVSS Server started on {self.host}:{self.port}")
            self.safe_log("Waiting for connections... (Press Ctrl+C to stop)")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.stats['connections'] += 1
                    self.safe_log(f"Connection from {address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    # Timeout is expected, just continue the loop
                    continue
                except socket.error:
                    if self.running:
                        self.safe_log("Error accepting connection")
                    
        except Exception as e:
            self.safe_log(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the KVSS server"""
        self.safe_log("\nShutting down server...")
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.safe_log("Server stopped")
    
    def handle_client(self, client_socket, address):
        """Handle client connection and requests"""
        buffer = ""  # Buffer to accumulate incomplete commands
        try:
            with client_socket:
                while self.running:
                    # Receive data from client
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    # Add received data to buffer
                    buffer += data
                    
                    # Process complete lines (ending with \n)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:  # Only process non-empty lines
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.safe_log(f"[{timestamp}] [REQUEST] from {address}: {line}")
                            response = self.process_request(line)
                            self.safe_log(f"[{timestamp}] [RESPONSE] to {address}: {response}")
                            client_socket.send(f"{response}\n".encode('utf-8'))
                            
                            # Close connection if QUIT command was processed
                            if self.is_quit_command(line):
                                self.safe_log(f"Client {address} sent QUIT command, closing connection")
                                buffer = ""  # Clear buffer before closing
                                return  # Exit the function, which closes the connection
                    
                    # Clear buffer if it gets too large (prevent memory issues)
                    if len(buffer) > 4096:  # 4KB limit
                        self.safe_log(f"Buffer overflow from {address}, clearing buffer")
                        buffer = ""
        except ConnectionResetError:
            self.safe_log(f"Client {address} disconnected")
        except Exception as e:
            self.safe_log(f"Error handling client {address}: {e}")
        finally:
            self.safe_log(f"Connection with {address} closed")
    
    def process_request(self, request):
        """Process a single request and return response"""
        self.stats['commands_processed'] += 1
        
        try:
            parts = request.split()
            if len(parts) < 2:
                return "400 BAD_REQUEST"
            
            version = parts[0].strip()
            command = parts[1].strip()
            
            # Check version
            if version != "KV/1.0":
                return "426 UPGRADE_REQUIRED"
            
            # Process commands
            if command == "PUT":
                return self.handle_put(parts[2:])
            elif command == "GET":
                return self.handle_get(parts[2:])
            elif command == "DEL":
                return self.handle_del(parts[2:])
            elif command == "STATS":
                return self.handle_stats()
            elif command == "QUIT":
                return self.handle_quit()
            else:
                return "400 BAD_REQUEST"
                
        except Exception as e:
            self.safe_log(f"Error processing request '{request}': {e}")
            return "500 SERVER_ERROR"
    
    def is_quit_command(self, request):
        """Check if the request is a QUIT command"""
        try:
            parts = request.split()
            return len(parts) >= 2 and parts[0] == "KV/1.0" and parts[1] == "QUIT"
        except:
            return False
    
    def handle_put(self, args):
        """Handle PUT command: KV/1.0 PUT key value"""
        self.stats['put_requests'] += 1
        
        if len(args) < 2:
            return "400 BAD_REQUEST"
        
        key = args[0]
        value = ' '.join(args[1:])  # Value can contain spaces
        
        # Check if key already exists
        if key in self.data_store:
            self.data_store[key] = value
            return "200 OK"
        else:
            self.data_store[key] = value
            return "201 CREATED"
    
    def handle_get(self, args):
        """Handle GET command: KV/1.0 GET key"""
        self.stats['get_requests'] += 1
        
        if len(args) != 1:
            return "400 BAD_REQUEST"
        
        key = args[0]
        
        if key in self.data_store:
            return f"200 OK {self.data_store[key]}"
        else:
            return "404 NOT_FOUND"
    
    def handle_del(self, args):
        """Handle DEL command: KV/1.0 DEL key"""
        self.stats['del_requests'] += 1
        
        if len(args) != 1:
            return "400 BAD_REQUEST"
        
        key = args[0]
        
        if key in self.data_store:
            del self.data_store[key]
            return "204 NO_CONTENT"
        else:
            return "404 NOT_FOUND"
    
    def handle_stats(self):
        """Handle STATS command: KV/1.0 STATS"""
        uptime = datetime.now() - self.stats['start_time']
        stats_data = [
            f"keys={len(self.data_store)}",
            f"uptime={round(uptime.total_seconds(), 3)}",
            f"served={self.stats['connections']}",
        ]
        return f"200 OK {' '.join(stats_data)}"
    
    def handle_quit(self):
        """Handle QUIT command: KV/1.0 QUIT"""
        return "200 OK goodbye"


def main():
    # Default values
    host = '127.0.0.1'
    port = 5050
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number", flush=True)
            sys.exit(1)
    
    # Create and start server
    server = KVSSServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        pass  # KeyboardInterrupt is handled in server.start()
    finally:
        server.stop()


if __name__ == "__main__":
    main()
