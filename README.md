# CSEE 4119 Spring 2025 — Final Project  
**Anya Chan (agc2173), Evelyn Cheng (ec3664), Rahi Mitra (rm3819)**

## GitHub Repository  
[https://github.com/anyagchan/audit-blocks](https://github.com/anyagchan/audit-blocks)

## Structure of the Code
- **`peer.py`**: Implementation for peer node logic 
- **`tracker.py`**: Central tracker that keeps track of a list of all active peers and broadcasts updates
- **`blockchain.py`**: Implementations for Block and Transaction classes, mining, Merkle root, PoW 
- **`demo_api.py`**: API endpoints for the demo application
- **`frontend/`**: contains the frontend components for the demo application, demo application design
- **`DESIGN.md`**:  describes the blockchain design, p2p protocol, 
- **`TESTING.md`**: describes the set of tests for demonstrating blockchain resilience

## Compilation
No other dependencies are required for compilation

## Usage of the Code
# Run the Tracker: 
   python tracker.py
# Starting peers: 
    python peer.py <peer_port> <tracker_ip> <tracker_port>
    
    python peer.py 10001 127.0.0.1 9000
    python peer.py 10002 127.0.0.1 9000
# Starting the frontend application
   npm start
