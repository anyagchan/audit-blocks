# DESIGN.md

## Project Overview

A peer-to-peer blockchain for garment factories that immutably logs signed shift records. Allows workers to log their hours and their managers to sign off on declared hours. Blockchain implementation prevents fraud and modification of hours.

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

## Features

1. Implementation of a peer-to-peer network with 1 tracker and at least 3 clients/peers
2. Implementation of a basic blockchain, where each node can

- maintain a copy of blockchain;
- create a valid block through mining;
- broadcast the block to other peers;
- verify a block and add it to the local blockchain;
- deal with forksLinks to an external site. where there are more than one branch in the network (happens when two or more peers mined a block at a similar time).

3. Implementation of a demo application using the blockchain for logging worker shifts
4. Transaction and block validation
5. Dynamic adjustment of mining difficulty based on the available computation power
6. Including multiple transactions inside a block and verify a transaction using Merkle tree

## Consensus & Proof-of-Work

- **Mining**: Peers vary the `nonce` until the block hash satisfies:
  ```
  SHA256(index ∥ prev_hash ∥ merkle_root ∥ timestamp ∥ nonce).startswith("0" * difficulty)
  ```
- **Difficulty Adjustment**: Every 10 blocks, the difficulty is recalibrated based on the actual time taken to mine the last 10 blocks vs. the expected time (1 block per minute). Adjustments scale the difficulty proportionally, with a lower bound of 1.
- **Fork Resolution**: When multiple forks exist, peers adopt the chain with the greatest cumulative difficulty (i.e., sum of block difficulties). If a stronger chain is received, peers rollback and replace their current chain accordingly.

---

## Peer-to-Peer Network

### Tracker Service

Central registry that maintains a live list of connected peers.

- `JOIN`: Peer registers its IP and port and receives the current peer list
- `LEAVE`: Peer deregisters before disconnecting
- `HEARTBEAT`: Periodic message (every 10 seconds) to indicate liveness

### Peer Messaging (JSON over TCP)

- `NEW_BLOCK`: Broadcast newly mined block, including full metadata and transactions
- `REQUEST_CHAIN`: Request all blocks starting from a given index
- `RESPONSE_CHAIN`: Return a sequence of blocks in response to a request

**Block Validation Flow**:

1. Validate Merkle root and proof-of-work
2. If the parent block is unknown, store as orphan
3. Store the block, update cumulative difficulty
4. If chain becomes stronger, switch and propagate
5. Rebroadcast to other peers

---

## Demo Application

### Roles & Authentication

- **Worker**: Logs hours with timestamps, date, etc.
- **Manager**: Signs off on hours declared by worker

### Shift Entry Flow

1. Worker logs shift start/end time
2. Worker signs the entry → `worker_signature`
3. Supervisor reviews and co-signs → `supervisor_signature`
4. Signed transaction is added to the local mempool
5. Peers mine pending transactions and broadcast them to the network

### Mining & Propagation

- Pending transactions are stored in each peer’s `mempool`
- Mining occurs on a timer
- Valid blocks are broadcast via `NEW_BLOCK`
- Receiving peers validate and append them, triggering fork resolution if necessary
