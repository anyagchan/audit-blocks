import socket
import threading
import json
import time
import sys
import atexit
from blockchain import Block, Transaction
import random

peer_state = {"peers": [], "blockchain": []}
mempool = []
DIFFICULTY = 3
block_map = {}
child_to_parent = {}
orphans = {}

def register_with_tracker(tracker_ip, tracker_port, my_port):
    msg = json.dumps({"type": "JOIN", "port": my_port})
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tracker_ip, tracker_port))
    s.sendall(msg.encode())
    response = s.recv(4096)
    peer_state["peers"] = json.loads(response.decode())["peers"]
    s.close()
    print("[PEER] Joined network. Peer list:", peer_state["peers"])

def periodically_refresh_peers(tracker_ip, tracker_port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((tracker_ip, tracker_port))
            s.sendall(json.dumps({"type": "GET"}).encode())
            data = s.recv(4096)
            peer_state["peers"] = json.loads(data.decode())["peers"]
            print("[PEER] Updated peer list:", peer_state["peers"])
            s.close()
        except Exception as e:
            print("Error refreshing peers:", e)
        time.sleep(10)

def leave_network(tracker_ip, tracker_port, my_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((tracker_ip, tracker_port))
        s.sendall(json.dumps({"type": "LEAVE", "port": my_port}).encode())
        s.close()
    except:
        pass

def start_peer_server(my_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', my_port))
    s.listen()
    print(f"[PEER] Listening on port {my_port}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_peer_connection, args=(conn, addr)).start()

def handle_peer_connection(conn, addr):
    try:
        data = conn.recv(4096).decode()
        msg = json.loads(data)
        print(f"[PEER] Received from {addr}: {msg}")

        if msg["type"] == "NEW_BLOCK":
            block = msg["block"]
            block_hash = block["hash"]
            prev_hash = block["prev_hash"]

            if block_hash in block_map:
                print("[PEER] Duplicate block received, ignoring.")
                return

            if prev_hash != "0" * 64 and prev_hash not in block_map:
                orphans[block_hash] = block
                print(f"[PEER] Received orphan block {block_hash[:6]}..., waiting for parent.")
                return

            block_map[block_hash] = block
            child_to_parent[block_hash] = prev_hash
            resolve_chain(block_hash)
            print("[PEER] Chain reorganized. Current height:", len(peer_state["blockchain"]))
            broadcast_to_peers(msg)

            unblock_orphans(block_hash)

        elif msg["type"] == "PING":
            conn.sendall(json.dumps({"type": "PONG"}).encode())

    except Exception as e:
        print("[PEER] Error handling peer:", e)
    finally:
        conn.close()

def broadcast_to_peers(msg):
    for peer in peer_state["peers"]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer["ip"], peer["port"]))
            s.sendall(json.dumps(msg).encode())
            s.close()
        except:
            continue

def mine_block():
    if not mempool:
        print("[MINER] No transactions to mine.")

    prev_block = peer_state["blockchain"][-1] if peer_state["blockchain"] else None
    prev_hash = prev_block["hash"] if prev_block else "0" * 64
    index = prev_block["index"] + 1 if prev_block else 0

    if prev_block and any(tx in prev_block["transactions"] for tx in [tx.to_dict() for tx in mempool]):
        print("[MINER] Transactions already included in last block. Skipping mining.")
        return

    block = Block(index, prev_hash, mempool[:], DIFFICULTY)
    print(f"[MINER] Mining block #{index}...")
    block.mine()
    print(f"[MINER] Mined block #{index}: {block.hash}")

    block_dict = block_to_dict(block)
    block_map[block_dict["hash"]] = block_dict
    child_to_parent[block_dict["hash"]] = block_dict["prev_hash"]

    resolve_chain(block_dict["hash"])
    broadcast_to_peers({"type": "NEW_BLOCK", "block": block_dict})

    mined_tx_dicts = [tx.to_dict() for tx in block.transactions]
    mempool[:] = [tx for tx in mempool if tx.to_dict() not in mined_tx_dicts]

def block_to_dict(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "prev_hash": block.prev_hash,
        "transactions": [tx.to_dict() for tx in block.transactions],
        "difficulty": block.difficulty,
        "nonce": block.nonce,
        "merkle_root": block.merkle_root,
        "hash": block.hash
    }

def miner_loop():
    while True:
        time.sleep(60)
        mine_block()

def resolve_chain(tip_hash):
    new_chain = []
    seen = set()
    current = tip_hash

    while current != "0" * 64:
        if current in seen or current not in block_map:
            print("[PEER] Incomplete or cyclic chain, aborting.")
            return
        seen.add(current)
        block = block_map[current]
        new_chain.append(block)
        current = block["prev_hash"]

    new_chain.reverse()
    if len(new_chain) > len(peer_state["blockchain"]):
        peer_state["blockchain"] = new_chain
        print("[PEER] Switched to longer chain with length", len(new_chain))
    else:
        print("[PEER] Received shorter chain, ignoring.")

def unblock_orphans(parent_hash):
    unlocked = [h for h, b in orphans.items() if b["prev_hash"] == parent_hash]
    for orphan_hash in unlocked:
        orphan_block = orphans.pop(orphan_hash)
        block_map[orphan_hash] = orphan_block
        child_to_parent[orphan_hash] = orphan_block["prev_hash"]
        print(f"[PEER] Added previously orphaned block {orphan_hash[:6]}...")
        resolve_chain(orphan_hash)
        broadcast_to_peers({"type": "NEW_BLOCK", "block": orphan_block})
        unblock_orphans(orphan_hash)

if __name__ == "__main__":
    my_port = int(sys.argv[1])
    tracker_ip = sys.argv[2]
    tracker_port = int(sys.argv[3])

    register_with_tracker(tracker_ip, tracker_port, my_port)
    threading.Thread(target=periodically_refresh_peers, args=(tracker_ip, tracker_port), daemon=True).start()
    threading.Thread(target=start_peer_server, args=(my_port,), daemon=True).start()
    threading.Thread(target=miner_loop, daemon=True).start()

    if my_port == 10001:
        tx1 = Transaction("W001", "2025-05-02", "09:00", "17:00", "sigW", "sigS")
        mempool.append(tx1)
        print(f"[PEER:{my_port}] Hardcoded transaction added to mempool.")

        tx2 = Transaction("W004", "2025-05-02", "18:00", "22:00", "sigW4", "sigS4")
        mempool.append(tx2)
        print(f"[PEER:{my_port}] Second transaction added to mempool.")
    
    if my_port == 10002:
        tx = Transaction("W002", "2025-05-02", "09:00", "17:00", "sigW2", "sigS2")
        mempool.append(tx)
        print(f"[PEER:{my_port}] Hardcoded transaction added to mempool.")
    
    if my_port == 10003:
        tx = Transaction("W003", "2025-05-02", "09:00", "17:00", "sigW3", "sigS3")
        mempool.append(tx)
        print(f"[PEER:{my_port}] Hardcoded transaction added to mempool.")
    
    if my_port == 10004:
        # No new transaction—just mine on the longest available block
        print(f"[PEER:{my_port}] Ready to resolve forks by extending a known chain.")


    atexit.register(leave_network, tracker_ip, tracker_port, my_port)

    while True:
        time.sleep(60)
