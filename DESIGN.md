# DESIGN.md

## Project Overview
A peer-to-peer blockchain for garment factories that immutably logs signed shift records. Prevents timesheet fraud, supports real-time audits, and holds workers and supervisors accountable.

## Blockchain Data Model

### Block Header  
- **index**: height in chain  
- **timestamp**: UTC creation time  
- **prev_hash**: SHA-256 of prior header  
- **merkle_root**: root hash of all shift-log transactions  
- **nonce**: proof-of-work value  
- **difficulty**: current mining target  
- **hash**: SHA-256 over header fields  

### Shift-Log Transaction  
```json
{
  "worker_id": "W123",
  "date": "2025-04-21T08:00:00Z",
  "shift_start": "08:00",
  "shift_end": "20:00",
  "worker_signature": "…",
  "supervisor_signature": "…"
}
```
Dual ECDSA signatures; transactions batched into a Merkle tree so clients can obtain inclusion proofs without downloading the full chain.

## Consensus & Proof-of-Work
- **Mining**: vary nonce until  
  ```
  SHA256(index ∥ prev_hash ∥ merkle_root ∥ timestamp ∥ nonce) < target
  ```
- **Difficulty adjustment** every 10 blocks to target ~1 block/min.  
- **Forks** resolved by choosing the chain with greatest cumulative difficulty; peers roll back and reapply as needed.

## Peer-to-Peer Network

### Tracker Service  
Central directory of active peers.  
- **JOIN**: peer registers IP/port → broadcast updated list  
- **LEAVE**: peer deregisters → broadcast removal  
- **HEARTBEAT**: periodic keep-alive to detect offline nodes  

### Peer Messaging (JSON-RPC over TCP)  
- **NEW_BLOCK**: broadcast new block header + transactions  
- **REQUEST_CHAIN**: `{ "from_index": N }` to catch up  
- **RESPONSE_CHAIN**: sequence of blocks from requested index  
- **PING/PONG**: health checks  

On receiving NEW_BLOCK, peers validate PoW & Merkle root, append or enqueue out-of-order, then relay.

## Demo Application

### Roles & Authentication  
- **Worker** and **Supervisor**: each holds ECDSA keypair issued by factory CA  
- **Auditor/Manager**: read-only view of chain explorer and audit tools  
- Authentication via TLS client certificates.

### Shift Entry Flow  
1. Worker logs in and enters start/end times.  
2. Worker “Sign” invokes private key → worker_signature.  
3. Payload sent for supervisor review → supervisor_signature.  
4. Signed transaction broadcast to network.

### Mining & Propagation  
- Pending logs in each peer’s mempool.  
- Automatic or manual mining (~1 min intervals) packages transactions into a block.  
- New blocks broadcast via NEW_BLOCK; peers validate and append.

### Chain Explorer & Audit Dashboard  
- **Block List**: recent blocks with index, timestamp, miner ID.  
- **Transaction View**: expand blocks to see individual shift-logs and their Merkle proofs.  
- **Audit Reports**: filter by date, worker or supervisor; flag overlapping shifts or missing signatures.  
- **Export**: CSV/PDF of selected records.

## Security & Accountability
- All communication over TLS.  
- ECDSA-256 signatures with keys stored in HSMs or encrypted keystores.  
- Immutable ledger—any tampering invalidates subsequent blocks.  
- Anomaly detection flags overlapping shifts, invalid signatures, or abnormal block timings.
