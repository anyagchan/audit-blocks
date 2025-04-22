# DESIGN.md

## Project Overview

This project implements a **peer-to-peer blockchain system** designed to log and secure worker shift records in garment factories. The goal is to eliminate the risks of time manipulation, paper-based logs, and labor exploitation by creating a **tamper-proof, transparent, and verifiable logging system**.

The system includes:
- A custom blockchain protocol
- A peer-to-peer (P2P) network with a central tracker
- A demo application for logging worker hours and verifying entries

---

## Blockchain Design

### Block Structure

Each block contains:
- `timestamp`: Time the block was created
- `logs`: A list of shift logs (signed transactions)
- `prev_hash`: Hash of the previous block
- `nonce`: Value used to satisfy proof-of-work
- `hash`: Hash of this block’s contents (including the nonce)

### Shift Log (Transaction) Format

Each shift log represents a transaction:
```json
{
  "worker_id": "W123",
  "date": "2025-04-21",
  "hours": 12,
  "worker_signature": "signed_with_worker_private_key",
  "supervisor_signature": "signed_with_supervisor_private_key"
}

