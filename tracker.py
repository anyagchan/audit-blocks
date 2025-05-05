# tracker.py

import socket
import threading
import json
import time

peer_list = []      # each entry: { ip, port, last_seen }
TTL = 30            # seconds before we consider a peer dead

def handle_client(conn, addr):
    """
    Handle incoming connections from peers and process their messages.

    Args:
        conn (socket): The socket connection object.
        addr (tuple): The address (IP, port) of the connecting peer.
    """
    global peer_list
    try:
        data = conn.recv(1024).decode()
        msg  = json.loads(data)

        # — Heartbeat —
        if msg.get("type") == "HEARTBEAT":
            for p in peer_list:
                if p["ip"] == addr[0] and p["port"] == msg["port"]:
                    p["last_seen"] = time.time()
                    break
            conn.sendall(b"{}")
            return

        # — JOIN —
        if msg.get("type") == "JOIN":
            new_peer = {"ip": addr[0], "port": msg["port"], "last_seen": time.time()}
            if not any(p["ip"] == new_peer["ip"] and p["port"] == new_peer["port"]
                       for p in peer_list):
                peer_list.append(new_peer)
            print(f"[TRACKER] Peer joined: {new_peer}")
            conn.sendall(json.dumps({"peers": peer_list}).encode())
            broadcast_peer_list()

        # — LEAVE —
        elif msg.get("type") == "LEAVE":
            peer_list[:] = [
                p for p in peer_list
                if not (p["ip"] == addr[0] and p["port"] == msg["port"])
            ]
            print(f"[TRACKER] Peer left: {addr[0]}:{msg['port']}")
            conn.sendall(json.dumps({"status": "removed"}).encode())
            broadcast_peer_list()

        # — GET —
        elif msg.get("type") == "GET":
            conn.sendall(json.dumps({"peers": peer_list}).encode())

    except Exception as e:
        print("[TRACKER] Error handling client:", e)
    finally:
        conn.close()

def broadcast_peer_list():
    """
    Push the current list of known peers to every peer in the network.
    """
    for p in peer_list:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((p["ip"], p["port"]))
            s.sendall(json.dumps({
                "type": "UPDATE_PEERS",
                "peers": peer_list
            }).encode())
            s.close()
        except:
            pass

def prune_stale_peers():
    """
    Periodically remove peers that have not sent a heartbeat within the TTL window.
    """
    while True:
        now = time.time()
        before = len(peer_list)
        peer_list[:] = [p for p in peer_list if now - p["last_seen"] <= TTL]
        if len(peer_list) != before:
            print(f"[TRACKER] Pruned stale peers → {len(peer_list)} remaining")
            broadcast_peer_list()
        time.sleep(TTL)

def start_tracker(port=9000):
    """
    Start the tracker server to handle peer connections.

    Args:
        port (int): Port to listen on. Defaults to 9000.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))
    s.listen()
    print(f"[TRACKER] Listening on port {port}")

    threading.Thread(target=prune_stale_peers, daemon=True).start()

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()
