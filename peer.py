# peer.py

import socket
import threading
import json
import time
import sys
import atexit
import hashlib
from datetime import datetime
from blockchain import Block, Transaction

peer_state   = {"peers": [], "blockchain": []}
mempool      = []
DIFFICULTY   = 3
block_map    = {}
child_to_parent = {}
orphans      = {}

def adjust_difficulty(chain, window=10, target_seconds=60):
    if len(chain) < window + 1:
        return DIFFICULTY
    last = chain[-1]
    prev = chain[-(window+1)]
    actual = (datetime.fromisoformat(last["timestamp"]) -
              datetime.fromisoformat(prev["timestamp"])).total_seconds()
    expected = target_seconds * window
    diff = last.get("difficulty", DIFFICULTY)
    return max(1, int(diff * (actual / expected)))

def register_with_tracker(tracker_ip, tracker_port, my_port):
    msg = json.dumps({"type": "JOIN", "port": my_port})
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tracker_ip, tracker_port))
    s.sendall(msg.encode())
    resp = s.recv(4096)
    peer_state["peers"] = json.loads(resp.decode())["peers"]
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
            s.close()
            print("[PEER] Refreshed peer list:", peer_state["peers"])
        except Exception as e:
            print("[PEER] Error refreshing peers:", e)
        time.sleep(10)

def send_heartbeat(tracker_ip, tracker_port, my_port):
    """Heartbeat to tracker every 10s."""
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((tracker_ip, tracker_port))
            s.sendall(json.dumps({"type": "HEARTBEAT", "port": my_port}).encode())
            s.close()
        except:
            pass
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
    s.bind(("0.0.0.0", my_port))
    s.listen()
    print(f"[PEER] Listening on port {my_port}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_peer_connection, args=(conn, addr)).start()

def handle_peer_connection(conn, addr):
    try:
        data = conn.recv(65536).decode()
        msg  = json.loads(data)

        # — Pushed peer-list update from tracker —
        if msg.get("type") == "UPDATE_PEERS":
            peer_state["peers"] = msg["peers"]
            print("[PEER] Received updated peer list:", peer_state["peers"])
            return

        if msg.get("type") == "NEW_BLOCK":
            block = msg["block"]
            h     = block["hash"]
            prev  = block["prev_hash"]

            # 1) Duplicate?
            if h in block_map:
                return

            # 2) Merkle-root check
            def compute_merkle(tx_list):
                tx_hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
                             for tx in tx_list]
                while len(tx_hashes) > 1:
                    nl = []
                    for i in range(0, len(tx_hashes), 2):
                        L = tx_hashes[i]
                        R = tx_hashes[i+1] if i+1 < len(tx_hashes) else L
                        nl.append(hashlib.sha256((L+R).encode()).hexdigest())
                    tx_hashes = nl
                return tx_hashes[0] if tx_hashes else ''
            if compute_merkle(block["transactions"]) != block["merkle_root"]:
                print("[PEER] Invalid Merkle root — rejecting", h[:6])
                return

            # 3) PoW check
            hdr = f'{block["index"]}{prev}{block["merkle_root"]}{block["timestamp"]}{block["nonce"]}'
            if hashlib.sha256(hdr.encode()).hexdigest() != h \
               or not h.startswith("0"*block["difficulty"]):
                print("[PEER] Invalid PoW — rejecting", h[:6])
                return

            # 4) Orphan?
            if prev != "0"*64 and prev not in block_map:
                orphans[h] = block
                print(f"[PEER] Received orphan {h[:6]}…")
                return

            # 5) Cumulative difficulty
            parent_cd = block_map.get(prev, {}).get("cum_diff", 0)
            block["cum_diff"] = parent_cd + block["difficulty"]

            # Append & propagate
            block_map[h] = block
            child_to_parent[h] = prev
            resolve_chain(h)
            broadcast_to_peers(msg)
            unblock_orphans(h)

        elif msg.get("type") == "REQUEST_CHAIN":
            idx = msg.get("from_index", 0)
            blks = [b for b in peer_state["blockchain"] if b["index"] >= idx]
            conn.sendall(json.dumps({"type":"RESPONSE_CHAIN","blocks":blks}).encode())

        elif msg.get("type") == "RESPONSE_CHAIN":
            for b in msg["blocks"]:
                block_map[b["hash"]] = b
                child_to_parent[b["hash"]] = b["prev_hash"]
            if msg["blocks"]:
                resolve_chain(msg["blocks"][-1]["hash"])

        elif msg.get("type") == "PING":
            conn.sendall(json.dumps({"type": "PONG"}).encode())

    except Exception as e:
        print("[PEER] Error:", e)
    finally:
        conn.close()

def broadcast_to_peers(msg):
    for p in peer_state["peers"]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((p["ip"], p["port"]))
            s.sendall(json.dumps(msg).encode())
            s.close()
        except:
            pass

def mine_block():
    if not mempool:
        return
    prev = peer_state["blockchain"][-1] if peer_state["blockchain"] else None
    prev_hash = prev["hash"] if prev else "0"*64
    idx = prev["index"]+1 if prev else 0

    difficulty = adjust_difficulty(peer_state["blockchain"])
    blk = Block(idx, prev_hash, mempool[:], difficulty)
    print(f"[MINER] Mining #{idx} (diff={difficulty})…")
    blk.mine()
    print(f"[MINER] Mined block #{idx}: {blk.hash}")

    bd = {
        "index": blk.index,
        "timestamp": blk.timestamp,
        "prev_hash": blk.prev_hash,
        "transactions": [tx.to_dict() for tx in blk.transactions],
        "difficulty": blk.difficulty,
        "nonce": blk.nonce,
        "merkle_root": blk.merkle_root,
        "hash": blk.hash,
        "cum_diff": 0
    }

    block_map[bd["hash"]] = bd
    child_to_parent[bd["hash"]] = bd["prev_hash"]
    resolve_chain(bd["hash"])
    broadcast_to_peers({"type":"NEW_BLOCK","block":bd})
    mempool[:] = [tx for tx in mempool if tx.to_dict() not in bd["transactions"]]

def miner_loop():
    while True:
        time.sleep(60)
        mine_block()

def resolve_chain(tip_hash):
    """Pick the chain with highest cumulative difficulty."""
    new_chain = []
    cur = tip_hash
    seen = set()
    while cur != "0"*64 and cur in block_map and cur not in seen:
        seen.add(cur)
        new_chain.append(block_map[cur])
        cur = block_map[cur]["prev_hash"]
    new_chain.reverse()

    new_cd = sum(b["difficulty"] for b in new_chain)
    old_cd = sum(b["difficulty"] for b in peer_state["blockchain"])
    if new_cd > old_cd:
        peer_state["blockchain"] = new_chain
        print(f"[PEER] Switched to chain (cum-diff={new_cd})")

def unblock_orphans(parent_hash):
    for h, b in list(orphans.items()):
        if b["prev_hash"] == parent_hash:
            del orphans[h]
            print(f"[PEER] Reintegrating orphan {h[:6]}…")
            block_map[h] = b
            child_to_parent[h] = b["prev_hash"]
            resolve_chain(h)
            broadcast_to_peers({"type":"NEW_BLOCK","block":b})
            unblock_orphans(h)

def sync_chain_on_startup(my_port):
    time.sleep(2)
    for p in peer_state["peers"]:
        if p["port"] == my_port:
            continue
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((p["ip"], p["port"]))
            s.sendall(json.dumps({"type":"REQUEST_CHAIN","from_index":0}).encode())
            resp = json.loads(s.recv(65536).decode())
            for b in resp.get("blocks", []):
                block_map[b["hash"]] = b
                child_to_parent[b["hash"]] = b["prev_hash"]
            if resp.get("blocks"):
                resolve_chain(resp["blocks"][-1]["hash"])
            s.close()
            break
        except:
            continue

def run_peer(my_port, tracker_ip, tracker_port):
    register_with_tracker(tracker_ip, tracker_port, my_port)
    threading.Thread(target=periodically_refresh_peers, args=(tracker_ip, tracker_port), daemon=True).start()
    threading.Thread(target=send_heartbeat, args=(tracker_ip, tracker_port, my_port), daemon=True).start()
    threading.Thread(target=start_peer_server, args=(my_port,), daemon=True).start()
    threading.Thread(target=miner_loop, daemon=True).start()
    threading.Thread(target=sync_chain_on_startup, args=(my_port,), daemon=True).start()

    # # Optional test TXs
    if my_port == 10001:
        mempool.append(Transaction("W001","2025-05-02","09:00","17:00","sigW","sigS"))
    # elif my_port == 10002:
    #     mempool.append(Transaction("W002","2025-05-02","09:00","17:00","sigW2","sigS2"))

    atexit.register(leave_network, tracker_ip, tracker_port, my_port)
    while True:
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <tracker_ip> <tracker_port>")
        sys.exit(1)
    run_peer(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
