## TESTING.md

This document outlines the manual test cases used to validate the functionality of our peer-to-peer blockchain and demo application, following the project specification.

# 1. Implementation of a peer-to-peer network

## Command:

python3 tracker.py
python3 demo_api.py 10001 127.0.0.1 9000 9001
python3 demo_api.py 10002 127.0.0.1 9000 9002
python3 demo_api.py 10003 127.0.0.1 9000 9003

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
python3 demo_api.py 10001 127.0.0.1 9000 9001
python3 demo_api.py 10002 127.0.0.1 9000 9002
python3 demo_api.py 10003 127.0.0.1 9000 9003

### Add transaction to Peer 1

echo "[1] Submitting to Peer 10001..."
curl -s -X POST http://127.0.0.1:9001/submit -H "Content-Type: application/json" -d '{
"username": "worker1",
"password": "pass1",
"date": "2025-05-04",
"shift_start": "08:00",
"shift_end": "16:00",
"worker_signature": "sigX"
}' > /dev/null

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

### Peer 3:

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

# 3. Testing fork resolution

## Command:

python3 tracker.py
python3 demo_api.py 10001 127.0.0.1 9000 9001
python3 demo_api.py 10002 127.0.0.1 9000 9002

### Start peer 1 and peer 2 with blocks (hardcoded for testing purposes)

if my_port == 10001:
tx1 = Transaction("W001","2025-05-02","09:00","17:00","sigW","sigS")
blk1 = Block(0, "0"\*64, [tx1], 3); blk1.mine()
blk2 = Block(1, blk1.hash, [tx1], 3); blk2.mine()

    peer_state["blockchain"] = [blk1.to_dict(), blk2.to_dict()]
    for blk in peer_state["blockchain"]:
        block_map[blk["hash"]] = blk
        child_to_parent[blk["hash"]] = blk["prev_hash"]

elif my_port == 10002:
tx2 = Transaction("W002","2025-05-02","09:00","17:00","sigW2","sigS2")
blk1b = Block(0, "0"\*64, [tx2], 3); blk1b.mine()
blk2b = Block(1, blk1b.hash, [tx2], 2); blk2b.mine()

    peer_state["blockchain"] = [blk1b.to_dict(), blk2b.to_dict()]
    for blk in peer_state["blockchain"]:
        block_map[blk["hash"]] = blk
        child_to_parent[blk["hash"]] = blk["prev_hash"]

## Output:

### Tracker:

[TRACKER] Listening on port 9000
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471658.574683}
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471661.032119}
[TRACKER] Peer left: 127.0.0.1:10002
[TRACKER] Peer left: 127.0.0.1:10001

### Peer 1:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471658.574683}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471658.574683}]
[PEER] Listening on port 10001
...
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471658.5760481}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471661.032119}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471668.5889668}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471661.0389628}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471678.594347}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471671.043008}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471678.594347}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471681.045543}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471688.599046}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471691.048568}]
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471698.604001}]

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746471658.5760481}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746471661.032119}]
[PEER] Listening on port 10002
...
[PEER] Switched to chain (cum-diff=6)
...

## Expected Output:

Both peers started with separate chains where peer 1 had a difficulty of 1 and peer 2 had a difficulty of 5. When they joined the network, peer 2 switched to peer 1's chain as shown by the switched to chain log so they now have identical chains. Peer 1 continues with it's chain and does not have the swiched chain log.

### Requirements met:

- deal with forks. where there are more than one branch in the network (happens when two or more peers mined a block at a similar time)

# 4. Invalid Merkle Root

## Command:

python3 tracker.py
python3 demo_api.py 10001 127.0.0.1 9000 9001
python3 demo_api.py 10002 127.0.0.1 9000 9002

### Add transaction to Peer 1

echo "[1] Submitting to Peer 10001..."
curl -s -X POST http://127.0.0.1:9001/submit -H "Content-Type: application/json" -d '{
"username": "worker1",
"password": "pass1",
"date": "2025-05-04",
"shift_start": "08:00",
"shift_end": "16:00",
"worker_signature": "sigX"
}' > /dev/null

### in handle_peer_connection() set invalid Merkle

block["merkle_root"] = "1234badroot"

## Output:

### Tracker:

[TRACKER] Listening on port 9000
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746480886.464993}
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746480889.479598}
[TRACKER] Peer left: 127.0.0.1:10001
[TRACKER] Peer left: 127.0.0.1:10002

### Peer 1:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746480886.464993}]
[PEER] Listening on port 10001
...
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746480886.46802}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746480889.479598}]
...
[MINER] Mining #0 (diff=3)…
[MINER] Mined block #0: 0004ed0b379aa4b1e0e9f9014b6f7e325a7bb4e02e6bfd27506d3def4ed425b0
[PEER] Switched to chain (cum-diff=3)

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746480886.46802}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746480889.479598}]
[PEER] Listening on port 10002
...
[PEER] Invalid Merkle root — rejecting 0004ed
...

## Expected Output:

After peer 2 receives the block mined by peer 1 it computes the Merkle root to validate and when it finds that it is incorrect, logs that it is invalid and rejects it. Note that the switch to chain log is not present because it rejected the block.

### Requirements met:

- Demonstration of how blockchain is resilient to invalid transactions

# 5. Modified Block

## Command:

python3 tracker.py
python3 demo_api.py 10001 127.0.0.1 9000 9001
python3 demo_api.py 10002 127.0.0.1 9000 9002

### Add transaction to Peer 1

echo "[1] Submitting to Peer 10001..."
curl -s -X POST http://127.0.0.1:9001/submit -H "Content-Type: application/json" -d '{
"username": "worker1",
"password": "pass1",
"date": "2025-05-04",
"shift_start": "08:00",
"shift_end": "16:00",
"worker_signature": "sigX"
}' > /dev/null

### in mine_block() change shift end timestamp

bd["transactions"][0]["shift_end"] = "23:59"

## Output:

### Tracker:

[TRACKER] Listening on port 9000
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.644804}
[TRACKER] Peer joined: {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746481453.871542}
[TRACKER] Peer left: 127.0.0.1:10002
[TRACKER] Peer left: 127.0.0.1:10001

### Peer 1:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.644804}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.644804}]
[PEER] Listening on port 10001
...
[PEER] Received updated peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.6456919}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746481453.871542}]
...
[MINER] Mining #0 (diff=3)…
[MINER] Mined block #0: 0001f9868157181b76983fae35301b90ef05f5756925f3ae65e2117faeec1bd4
[PEER] Switched to chain (cum-diff=3)
...

### Peer 2:

[PEER] Joined network. Peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.6456919}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746481453.871542}]
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481451.6456919}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746481453.871542}]
[PEER] Listening on port 10002
...
[PEER] Invalid Merkle root — rejecting 0001f9
[PEER] Refreshed peer list: [{'ip': '127.0.0.1', 'port': 10001, 'last_seen': 1746481511.684423}, {'ip': '127.0.0.1', 'port': 10002, 'last_seen': 1746481513.902771}]

## Expected Output:

After peer 2 receives the block mined by peer 1 it computes the Merkle root to validate it and when it finds that the Merkle root associated with it doesn't match the transaction details, it rejects the block.

### Requirements met:

- Demonstration of how blockchain is resilient to modifications made to blocks
