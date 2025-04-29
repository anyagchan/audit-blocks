import socket
import threading
import json

PEERS = []
MEMPOOL = []

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        while data := conn.recv(4096):
            msg = json.loads(data.decode())
            print("Received:", msg)
            # Handle messages: NEW_BLOCK, REQUEST_CHAIN, etc.
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

def start_peer(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen()
    print(f"Peer listening on port {port}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    start_peer(port)
