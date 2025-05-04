# demo_api.py

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from peer import run_peer, mempool, peer_state, mine_block, broadcast_to_peers
from blockchain import Transaction
import threading, sys, csv, ssl, copy
from io import StringIO

app = Flask(__name__)
CORS(app)

USERS = {
    'worker1': ('pass1', 'worker'),
    'manager1': ('pass2', 'manager')
}

def authenticate(data):
    u = data.get('username'); p = data.get('password')
    if u in USERS and USERS[u][0] == p:
        return USERS[u][1]
    return None

@app.route('/submit', methods=['POST'])
def submit_shift():
    data = request.get_json() or {}
    if authenticate(data) != 'worker':
        return jsonify({'error':'Unauthorized'}),403
    req = ['username','password','date','shift_start','shift_end','worker_signature']
    missing = [k for k in req if k not in data]
    if missing:
        return jsonify({'error':f'Missing: {missing}'}),400

    tx = Transaction(
        data['username'], data['date'],
        data['shift_start'], data['shift_end'],
        data['worker_signature'], ''
    )
    mempool.append(tx)
    mine_block()
    return jsonify({'status':'queued & mined'}),200

@app.route('/chain', methods=['GET'])
def view_chain():
    return jsonify(peer_state['blockchain']),200

@app.route('/approve', methods=['POST'])
def approve_shift():
    data = request.get_json() or {}
    if authenticate(data) != 'manager':
        return jsonify({'error':'Unauthorized'}),403
    bh = data.get('block_hash'); ti = data.get('tx_index')
    if bh is None or ti is None:
        return jsonify({'error':'block_hash & tx_index required'}),400
    for b in peer_state['blockchain']:
        if b['hash']==bh and 0<=ti<len(b['transactions']):
            b['transactions'][ti]['supervisor_signature']='Approved by manager1'
            return jsonify({'status':'approved'}),200
    return jsonify({'error':'Not found'}),404

@app.route('/reject', methods=['POST'])
def reject_shift():
    data = request.get_json() or {}
    if authenticate(data) != 'manager':
        return jsonify({'error':'Unauthorized'}),403
    bh = data.get('block_hash'); ti = data.get('tx_index')
    if bh is None or ti is None:
        return jsonify({'error':'block_hash & tx_index required'}),400
    for b in peer_state['blockchain']:
        if b['hash']==bh and 0<=ti<len(b['transactions']):
            b['transactions'][ti]['supervisor_signature']='Rejected by manager1'
            return jsonify({'status':'rejected'}),200
    return jsonify({'error':'Not found'}),404

@app.route('/export', methods=['GET'])
def export_chain():
    si = StringIO(); w = csv.writer(si)
    w.writerow(['block_index','timestamp','worker_id','date','start','end',
                'worker_signature','supervisor_signature','block_hash'])
    for b in peer_state['blockchain']:
        for tx in b['transactions']:
            w.writerow([
                b['index'], b['timestamp'],
                tx['worker_id'], tx['date'],
                tx['shift_start'], tx['shift_end'],
                tx['worker_signature'], tx.get('supervisor_signature',''),
                b['hash']
            ])
    out = make_response(si.getvalue())
    out.headers["Content-Disposition"]="attachment; filename=chain.csv"
    out.headers["Content-Type"]="text/csv"
    return out

@app.route('/anomalies', methods=['GET'])
def detect_anomalies():
    anomalies=[]; per_worker={}
    from datetime import datetime as dt
    for b in peer_state['blockchain']:
        for tx in b['transactions']:
            per_worker.setdefault(tx['worker_id'],[]).append(
                (tx['date'],tx['shift_start'],tx['shift_end'],b['index']))
    for w,shifts in per_worker.items():
        parsed=[]
        for date,s,e,idx in shifts:
            parsed.append((dt.fromisoformat(f"{date}T{s}"),
                           dt.fromisoformat(f"{date}T{e}"), idx))
        parsed.sort()
        for i in range(len(parsed)-1):
            s1,e1,i1 = parsed[i]; s2,e2,i2 = parsed[i+1]
            if s2<e1:
                anomalies.append({
                    'worker_id':w,'block1':i1,'block2':i2,
                    'overlap_start':s2.isoformat(),
                    'overlap_end':e1.isoformat()
                })
    return jsonify(anomalies),200

@app.route('/test-tamper', methods=['GET'])
def test_tamper():
    if not peer_state['blockchain']:
        return jsonify({'error':'no blocks'}),400
    blk = copy.deepcopy(peer_state['blockchain'][0])
    blk['transactions'][0]['worker_id']='TAMPER'
    broadcast_to_peers({'type':'NEW_BLOCK','block':blk})
    return jsonify({'status':'tamper attempt sent'}),200

if __name__ == '__main__':
    if len(sys.argv) not in (4,5):
        print('Usage: python demo_api.py <peer_port> <tracker_ip> <tracker_port> [<api_port>]')
        sys.exit(1)
    peer_port    = int(sys.argv[1])
    tracker_ip   = sys.argv[2]
    tracker_port = int(sys.argv[3])
    api_port     = int(sys.argv[4]) if len(sys.argv)==5 else 5000

    threading.Thread(target=run_peer,
                     args=(peer_port,tracker_ip,tracker_port),
                     daemon=True).start()

    # TLS setup (generate with: openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365)
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # context.load_cert_chain("server.crt", "server.key")

    app.run(host='0.0.0.0', port=api_port)