import socket
import threading
import json

peer_list = []

def handle_client(conn, addr):
    global peer_list
    try:
        data = conn.recv(1024).decode()
        msg = json.loads(data)

        if msg["type"] == "JOIN":
            new_peer = {"ip": addr[0], "port": msg["port"]}
            if new_peer not in peer_list:
                peer_list.append(new_peer)
            print(f"Peer joined: {new_peer}")
            conn.sendall(json.dumps({"peers": peer_list}).encode())

        elif msg["type"] == "LEAVE":
            peer_list[:] = [p for p in peer_list if not (p["ip"] == addr[0] and p["port"] == msg["port"])]
            print(f"Peer left: {addr[0]}:{msg['port']}")
            conn.sendall(json.dumps({"status": "removed"}).encode())

        elif msg["type"] == "GET":
            conn.sendall(json.dumps({"peers": peer_list}).encode())

    except Exception as e:
        print("Error handling client:", e)
    finally:
        conn.close()

def start_tracker(port=9000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen()
    print(f"[TRACKER] Listening on port {port}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()
