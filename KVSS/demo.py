#!/usr/bin/env python3
"""
Demo script showing KVSS usage examples
"""

import time
import subprocess
import sys
import os
from client import KVSSClient


def demo_basic_operations():
    """Demonstrate basic KVSS operations"""
    print("======================== Basic Operations Demo ========================")
    
    client = KVSSClient()
    if not client.connect():
        print("Failed to connect to server")
        return False
    
    try:
        # PUT operations
        print("KV/1.0 PUT user42 Alice")
        response = client.send_command("KV/1.0 PUT user42 Alice")
        print(f"Response: {response}")
        
        print("KV/1.0 GET user42")
        response = client.send_command("KV/1.0 GET user42")
        print(f"Response: {response}")
        
        print("KV/1.0 DEL user42")
        response = client.send_command("KV/1.0 DEL user42")
        print(f"Response: {response}")

        print("KV/1.0 GET user42")
        response = client.send_command("KV/1.0 GET user42")
        print(f"Response: {response}")

        print("KV/1.0 STATS")
        response = client.send_command("KV/1.0 STATS")
        print(f"Response: {response}")

        print("\n3. nhiều value:")
        print("KV/1.0 PUT user42 Alice EXTRA EXTRA")
        response = client.send_command("KV/1.0 PUT user42 Alice EXTRA EXTRA")
        print(f"Response: {response}")
        print("KV/1.0 GET user42")
        response = client.send_command("KV/1.0 GET user42")
        print(f"Response: {response}")

        
        print("KV/1.0 QUIT")
        response = client.send_command("KV/1.0 QUIT")
        print(f"Response: {response}")
        
        return True
        
    finally:
        client.disconnect()


def demo_error_cases():
    """Demonstrate error handling"""
    print("\n======================== Error Cases Demo ========================")
    
    client = KVSSClient()
    if not client.connect():
        print("Failed to connect to server")
        return False
    
    try:
        print("\n1. Thiếu version:")
        print("PUT user42 Alice")
        response = client.send_command("PUT user42 Alice")
        print(f"Response: {response}")
        
        print("\n2. Thiếu value:")
        print("PUT user42")
        response = client.send_command("PUT user42")
        print(f"Response: {response}")

        print("\n2. Sai method:")
        print("KV/1.0 POST user42 Alice")
        response = client.send_command("KV/1.0 POST user42 Alice")
        print(f"Response: {response}")
        
        return True
        
    finally:
        client.disconnect()


def demo_multiple_clients():
    """Demonstrate multiple client connections"""
    print("\n======================== Multiple Clients Demo ========================")
    
    # Client 1
    client1 = KVSSClient()
    if not client1.connect():
        print("Failed to connect client 1")
        return False
    
    # Client 2
    client2 = KVSSClient()
    if not client2.connect():
        print("Failed to connect client 2")
        client1.disconnect()
        return False
    
    try:
        print("\nClient 1 stores data:")
        print("KV/1.0 PUT shared_key value_from_client1")
        response = client1.send_command("KV/1.0 PUT shared_key value_from_client1")
        print(f"Client 1 response: {response}")
        
        print("\nClient 2 reads data:")
        print("KV/1.0 GET shared_key")
        response = client2.send_command("KV/1.0 GET shared_key")
        print(f"Client 2 response: {response}")
        
        print("\nClient 2 updates data:")
        print("KV/1.0 PUT shared_key value_from_client2")
        response = client2.send_command("KV/1.0 PUT shared_key value_from_client2")
        print(f"Client 2 response: {response}")
        
        print("\nClient 1 reads updated data:")
        print("KV/1.0 GET shared_key")
        response = client1.send_command("KV/1.0 GET shared_key")
        print(f"Client 1 response: {response}")
        
        return True
        
    finally:
        client1.disconnect()
        client2.disconnect()


def start_demo_server():
    """Start server for demo"""
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    return subprocess.Popen([sys.executable, server_script])


def main():
    print("KVSS Demo - Key-Value Store Service")
    print("=" * 50)
    
    print("Starting demo server...")
    server_process = start_demo_server()
    time.sleep(2)  # Give server time to start
    
    try:
        # Run demos
        demo_basic_operations()
        demo_error_cases()
        demo_multiple_clients()
        print("\nDemo completed successfully!")
    
    
    finally:
        print("\nStopping demo server...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()
