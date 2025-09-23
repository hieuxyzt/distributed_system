# Mini Key-Value Store Service (KVSS)

A simple TCP-based key-value store implementation following the distributed systems course requirements. This project demonstrates basic client-server architecture with a text-based protocol.

## Features

- **TCP Connection**: Default host:port 127.0.0.1:5050
- **Text-based Protocol**: Line-oriented messages ending with `\n` (LF)
- **UTF-8 Encoding**: Full Unicode support
- **Version Control**: KV/1.0 protocol version
- **Thread-safe**: Multiple concurrent client connections
- **In-memory Storage**: Fast key-value operations

## Protocol Specification

### Request Format
```
<version> " " <command> [ " " <args> ] "\n"
```

### Commands
- `KV/1.0 PUT <key> <value>` - Store key-value pair
- `KV/1.0 GET <key>` - Retrieve value for key
- `KV/1.0 DEL <key>` - Delete key-value pair
- `KV/1.0 STATS` - Show server statistics
- `KV/1.0 QUIT` - Disconnect from server

### Response Codes
- `200 OK [data]` - Success with optional data
- `201 CREATED` - Key created successfully (PUT new key)
- `204 NO_CONTENT` - Success with no content (DELETE)
- `400 BAD_REQUEST` - Invalid syntax or missing parameters
- `404 NOT_FOUND` - Key not found
- `426 UPGRADE_REQUIRED` - Missing or wrong protocol version
- `500 SERVER_ERROR` - Internal server error

## Files

- `server.py` - KVSS server implementation
- `client.py` - KVSS client with interactive mode
- `test_kvss.py` - Automated test suite
- `demo.py` - Usage demonstration script

## Quick Start

### 1. Start the Server
```bash
python server.py [host] [port]
```
Default: `python server.py` (starts on 127.0.0.1:5050)

### 2. Connect with Client
```bash
python client.py [host] [port] [command]
```

**Interactive Mode:**
```bash
python client.py
```

**Single Command:**
```bash
python client.py 127.0.0.1 5050 GET mykey
```

### 3. Manual Connection (Testing)
You can also connect manually using tools like `nc`, `telnet`, or `curl`:

```bash
# Using netcat
nc 127.0.0.1 5050

# Using telnet
telnet 127.0.0.1 5050

# Using PowerShell (Windows)
Test-NetConnection -ComputerName 127.0.0.1 -Port 5050
```

## Usage Examples

### Basic Operations
```
KVSS> PUT name John
201 CREATED

KVSS> GET name
200 OK John

KVSS> PUT name Jane
200 OK

KVSS> GET name
200 OK Jane

KVSS> DEL name
204 NO_CONTENT

KVSS> GET name
404 NOT_FOUND

KVSS> STATS
200 OK uptime: 0:05:23; connections: 1; commands_processed: 6; get_requests: 3; put_requests: 2; del_requests: 1; keys_stored: 0
```

### Error Handling
```
KVSS> GET
400 BAD_REQUEST

KVSS> PUT keyonly
400 BAD_REQUEST

KVSS> INVALID command
400 BAD_REQUEST

KVSS> WRONG/1.0 GET test
426 UPGRADE_REQUIRED
```

## Testing

### Run Automated Tests
```bash
python test_kvss.py
```

### Run Demo
```bash
python demo.py
```

## Network Analysis with Wireshark

To analyze the protocol packets:

1. Start Wireshark
2. Capture on loopback interface (127.0.0.1)
3. Filter: `tcp.port == 5050`
4. Start server and client
5. Observe the text-based protocol messages

Sample packet content:
```
Client → Server: KV/1.0 PUT mykey myvalue\n
Server → Client: 201 CREATED\n
```

## Architecture

### Server Architecture
- **Multi-threaded**: Each client connection handled in separate thread
- **In-memory storage**: Dictionary-based key-value store
- **Statistics tracking**: Connection count, command statistics, uptime
- **Error handling**: Graceful error responses and connection cleanup

### Client Architecture
- **Interactive mode**: Command-line interface with readline support
- **Batch mode**: Single command execution
- **Connection management**: Automatic connection handling
- **Protocol abstraction**: Automatic KV/1.0 prefix addition

## Protocol Implementation Details

### Message Format
- Each message is a single line terminated by `\n` (ASCII 10)
- UTF-8 encoding for full Unicode support
- Space-separated tokens
- Version prefix required for all requests

### Connection Handling
- TCP keep-alive connections
- Multiple commands per connection
- Graceful disconnection with QUIT command
- Automatic cleanup on client disconnect

### Data Storage
- In-memory hash table (Python dict)
- Keys: strings without spaces
- Values: strings (can contain spaces)
- No persistence (data lost on server restart)

## Extending the Implementation

### Adding Persistence
```python
import json

def save_data(self):
    with open('kvss_data.json', 'w') as f:
        json.dump(self.data_store, f)

def load_data(self):
    try:
        with open('kvss_data.json', 'r') as f:
            self.data_store = json.load(f)
    except FileNotFoundError:
        self.data_store = {}
```

### Adding Authentication
```python
def handle_auth(self, args):
    if len(args) != 2:
        return "400 BAD_REQUEST"
    username, password = args
    # Implement authentication logic
    return "200 OK authenticated"
```

### Adding TTL (Time To Live)
```python
import time

class TTLDict:
    def __init__(self):
        self.data = {}
        self.ttl = {}
    
    def put(self, key, value, ttl=None):
        self.data[key] = value
        if ttl:
            self.ttl[key] = time.time() + ttl
    
    def get(self, key):
        if key in self.ttl and time.time() > self.ttl[key]:
            del self.data[key]
            del self.ttl[key]
            return None
        return self.data.get(key)
```

## System Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
- Works on Windows, Linux, macOS

## Troubleshooting

### Common Issues

**Connection Refused:**
- Ensure server is running
- Check firewall settings
- Verify correct host and port

**Protocol Errors:**
- Ensure commands start with `KV/1.0`
- Check command syntax
- Use proper line endings (`\n`)

**Performance Issues:**
- Server uses threading for concurrency
- In-memory storage for fast access
- Consider connection pooling for many clients

## License

This project is for educational purposes as part of the Distributed Systems course.

## Course Information

- **Course**: Distributed Systems (IT4611)
- **Institution**: School of Information and Communication Technology (SoICT)
- **Topic**: Chapter 1 - System Architecture Overview
- **Implementation**: Mini Key-Value Store Service (KVSS)
