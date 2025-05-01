import socket
import threading
import json
import time
import sys
import atexit

peer_state = {"peers": [], "blockchain": []}

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
            peer_state["blockchain"].append(msg["block"])
            print("[PEER] New block added. Chain length:", len(peer_state["blockchain"]))
            broadcast_to_peers(msg)

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

if __name__ == "__main__":
    my_port = int(sys.argv[1])
    tracker_ip = sys.argv[2]
    tracker_port = int(sys.argv[3])

    register_with_tracker(tracker_ip, tracker_port, my_port)
    threading.Thread(target=periodically_refresh_peers, args=(tracker_ip, tracker_port), daemon=True).start()
    threading.Thread(target=start_peer_server, args=(my_port,), daemon=True).start()

    atexit.register(leave_network, tracker_ip, tracker_port, my_port)

    while True:
        time.sleep(60)
