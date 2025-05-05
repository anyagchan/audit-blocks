# blockchain.py

import hashlib
import json
from datetime import datetime
from ecdsa import SigningKey

WORKER_KEYS = {
    # "W001": VerifyingKey.from_pem(open("keys/W001_pub.pem").read())
}
SUPERVISOR_KEYS = {
    # "W001": VerifyingKey.from_pem(open("keys/S001_pub.pem").read())
}

class Transaction:
    """
    Represents a worker shift transaction including digital signatures
    from the worker and supervisor.
    """
    def __init__(self, worker_id, date, start, end, worker_sig='', supervisor_sig=''):
        """
        Initialize a new Transaction.

        Args:
            worker_id (str): The ID of the worker.
            date (str): The date of the shift.
            start (str): Start time of the shift.
            end (str): End time of the shift.
            worker_sig (str): Digital signature of the worker.
            supervisor_sig (str): Digital signature of the supervisor.
        """
        self.worker_id = worker_id
        self.date = date
        self.shift_start = start
        self.shift_end = end
        self.worker_signature = worker_sig
        self.supervisor_signature = supervisor_sig

    def to_dict(self):
        """
        Convert the transaction into a dictionary.

        Returns:
            dict: Dictionary representation of the transaction.
        """
        return {
            "worker_id": self.worker_id,
            "date": self.date,
            "shift_start": self.shift_start,
            "shift_end": self.shift_end,
            "worker_signature": self.worker_signature,
            "supervisor_signature": self.supervisor_signature
        }

    def sign_worker(self, sk: SigningKey):
        """
        Sign the transaction using the worker's private key.

        Args:
            sk (SigningKey): The signing key of the worker.
        """
        payload = json.dumps({
            "worker_id": self.worker_id,
            "date": self.date,
            "shift_start": self.shift_start,
            "shift_end": self.shift_end
        }, sort_keys=True).encode()
        self.worker_signature = sk.sign(payload).hex()

    def verify_worker(self):
        """
        Verify the worker's signature.

        Returns:
            bool: True if signature is valid, False otherwise.

        Raises:
            ValueError: If the worker's public key is not found.
        """
        vk = WORKER_KEYS.get(self.worker_id)
        if vk is None:
            raise ValueError(f"No public key for worker {self.worker_id}")
        payload = json.dumps({
            "worker_id": self.worker_id,
            "date": self.date,
            "shift_start": self.shift_start,
            "shift_end": self.shift_end
        }, sort_keys=True).encode()
        return vk.verify(bytes.fromhex(self.worker_signature), payload)

    def sign_supervisor(self, sk: SigningKey):
        """
        Sign the transaction using the supervisor's private key.

        Args:
            sk (SigningKey): The signing key of the supervisor.
        """
        payload = json.dumps(self.to_dict(), sort_keys=True).encode()
        self.supervisor_signature = sk.sign(payload).hex()

    def verify_supervisor(self):
        """
        Verify the supervisor's signature.

        Returns:
            bool: True if signature is valid, False otherwise.

        Raises:
            ValueError: If the supervisor's public key is not found.
        """
        vk = SUPERVISOR_KEYS.get(self.worker_id)
        if vk is None:
            raise ValueError(f"No public key for supervisor of {self.worker_id}")
        payload = json.dumps({
            "worker_id": self.worker_id,
            "date": self.date,
            "shift_start": self.shift_start,
            "shift_end": self.shift_end,
            "worker_signature": self.worker_signature
        }, sort_keys=True).encode()
        return vk.verify(bytes.fromhex(self.supervisor_signature), payload)

class Block:
    """
    Represents a block in the blockchain containing a list of transactions.
    """
    def __init__(self, index, prev_hash, transactions, difficulty):
        """
        Initialize a new Block.

        Args:
            index (int): The index of the block.
            prev_hash (str): Hash of the previous block.
            transactions (list): List of Transaction objects.
            difficulty (int): Proof-of-work difficulty.
        """
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.difficulty = difficulty
        self.nonce = 0
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.compute_hash()

    def compute_merkle_root(self):
        """
        Compute the Merkle root of the block's transactions.

        Returns:
            str: The Merkle root hash.
        """
        tx_hashes = [
            hashlib.sha256(json.dumps(tx.to_dict(), sort_keys=True).encode()).hexdigest()
            for tx in self.transactions
        ]
        while len(tx_hashes) > 1:
            new_level = []
            for i in range(0, len(tx_hashes), 2):
                L = tx_hashes[i]
                R = tx_hashes[i+1] if i+1 < len(tx_hashes) else L
                new_level.append(hashlib.sha256((L+R).encode()).hexdigest())
            tx_hashes = new_level
        return tx_hashes[0] if tx_hashes else ''

    def compute_hash(self):
        """
        Compute the block hash using SHA-256 over block header fields.

        Returns:
            str: The computed hash.
        """
        header = f'{self.index}{self.prev_hash}{self.merkle_root}{self.timestamp}{self.nonce}'
        return hashlib.sha256(header.encode()).hexdigest()

    def mine(self):
        """
        Perform proof-of-work to find a valid nonce that meets the difficulty requirement.
        """
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()

    def to_dict(self):
        """
        Convert the block into a dictionary.

        Returns:
            dict: Dictionary representation of the block.
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }
