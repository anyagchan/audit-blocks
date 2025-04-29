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
            peer = {"ip": addr[0], "port": msg["port"]}
            if peer not in peer_list:
                peer_list.append(peer)
            conn.sendall(json.dumps({"peers": peer_list}).encode())

        elif msg["type"] == "LEAVE":
            peer_list = [p for p in peer_list if not (p["ip"] == addr[0] and p["port"] == msg["port"])]
            conn.sendall(json.dumps({"status": "removed"}).encode())

        elif msg["type"] == "GET":
            conn.sendall(json.dumps({"peers": peer_list}).encode())

    except Exception as e:
        print("Tracker error:", e)
    finally:
        conn.close()

def start_tracker(port=9000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen()
    print(f"Tracker listening on port {port}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()
