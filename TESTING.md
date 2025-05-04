## TESTING.md

This document outlines the manual test cases used to validate the functionality of our peer-to-peer blockchain and demo application, following the project specification.

# 1. Implementation of a peer-to-peer network

## Command:

python3 tracker.py
python3 peer.py 10001 127.0.0.1 9000
python3 peer.py 10002 127.0.0.1 9000
python3 peer.py 10003 127.0.0.1 9000

## Output:

### Tracker:

[TRACKER] Listening on port 9000
Peer joined: {'ip': '127.0.0.1', 'port': 10001}
Peer joined: {'ip': '127.0.0.1', 'port': 10002}
Peer joined: {'ip': '127.0.0.1', 'port': 10003}
Peer left: 127.0.0.1:10003
Peer left: 127.0.0.1:10002
Peer left: 127.0.0.1:10001

### Peer 1:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001}]
[PEER] Listening on port 10001
[PEER] Updated peer list: [{'ip': '127.0.0.1', 'port': 10001}]
[PEER] Updated peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}, {'ip': '127.0.0.1', 'port': 10003}]

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}]
[PEER] Listening on port 10002
[PEER] Updated peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}]
[PEER] Updated peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}, {'ip': '127.0.0.1', 'port': 10003}]

### Peer 3:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}, {'ip': '127.0.0.1', 'port': 10003}]
[PEER] Listening on port 10003
[PEER] Updated peer list: [{'ip': '127.0.0.1', 'port': 10001}, {'ip': '127.0.0.1', 'port': 10002}, {'ip': '127.0.0.1', 'port': 10003}]

## Expected Output:

The logs demonstrate the list of peers being updated when a peer joins/leaves the network. Every peer's peer list is periodically updated when other peers join/leave the network.

### Requirements met:

- Tracker maintains a list of peers which is updated when a peer joins or leaves the network
- Every peer should be aware of any updates made to the list

# 2. Implementation of basic blockchain

## Command:

python3 tracker.py
python3 peer.py 10001 127.0.0.1 9000
python3 peer.py 10002 127.0.0.1 9000
python3 peer.py 10003 127.0.0.1 9000

### hardcoded into peer.py (for testing purposes only):

if my_port == 10001:
mempool.append(Transaction("W001","2025-05-02","09:00","17:00","sigW","sigS"))

## Output:

### Tracker:

[TRACKER] Listening on port 9000
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.596658}
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290216}
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10003, 'last_seen': 1746369523.821905}
[TRACKER] Peer left: 127.0.0.1:10003
[TRACKER] Peer left: 127.0.0.1:10001
[TRACKER] Peer left: 127.0.0.1:10002

### Peer 1:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.596658}]
[PEER] Listening on port 10001
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.596658}]
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290216}]
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290943}, {'ip': '127.0.0.1', 'port': 10003, 'last_seen': 1746369523.821905}]
...
[MINER] Mining #0 (diff=3)…
[MINER] Mined block #0: 00072babc46f5bdd30f35f22f1d31da5d3690d3a73374293aebb610d6cc63a80
[PEER] Switched to chain (cum-diff=3)
...

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290216}]
[PEER] Listening on port 10002
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290216}]
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290943}, {'ip': '127.0.0.1', 'port': 10003, 'last_seen': 1746369523.821905}]
...
[PEER] Switched to chain (cum-diff=3)
...

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290943}, {'ip': '127.0.0.1', 'port': 10003, 'last_seen': 1746369523.821905}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746369518.597406}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746369521.290943}, {'ip': '127.0.0.1', 'port': 10003, 'last_seen': 1746369523.821905}]
[PEER] Listening on port 10003
...
[PEER] Switched to chain (cum-diff=3)
...

## Expected Output:

The transaction is mined by peer 1 as shown by the logs and added to the blockchain. This addition is broadcasted to the other peers and a copy is maintained by all the peers as shown by the log "[PEER] Switched to chain (cum-diff=3)"

### Requirements met:

- maintain a copy of blockchain
- create a valid block through mining
- broadcast the block to other peers
- verify a block and add it to the local blockchain
