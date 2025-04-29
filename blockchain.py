import hashlib
import json
from datetime import datetime

class Transaction:
    def __init__(self, worker_id, date, start, end, worker_sig, supervisor_sig):
        self.worker_id = worker_id
        self.date = date
        self.shift_start = start
        self.shift_end = end
        self.worker_signature = worker_sig
        self.supervisor_signature = supervisor_sig

    def to_dict(self):
        return self.__dict__

class Block:
    def __init__(self, index, prev_hash, transactions, difficulty):
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.difficulty = difficulty
        self.nonce = 0
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.compute_hash()

    def compute_merkle_root(self):
        tx_hashes = [hashlib.sha256(json.dumps(tx.to_dict(), sort_keys=True).encode()).hexdigest()
                     for tx in self.transactions]
        while len(tx_hashes) > 1:
            new_level = []
            for i in range(0, len(tx_hashes), 2):
                left = tx_hashes[i]
                right = tx_hashes[i+1] if i+1 < len(tx_hashes) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                new_level.append(combined)
            tx_hashes = new_level
        return tx_hashes[0] if tx_hashes else ''

    def compute_hash(self):
        header = f'{self.index}{self.prev_hash}{self.merkle_root}{self.timestamp}{self.nonce}'
        return hashlib.sha256(header.encode()).hexdigest()

    def mine(self):
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()
