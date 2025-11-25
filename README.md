# Atmateh Scripts

Collection of monitoring and automation scripts.

## Substrate Sync Monitor

Monitors Substrate node sync status and sends notifications when nodes are fully synced.

### Features

- Real-time sync progress monitoring
- ETA calculation for full sync
- Sync rate tracking (blocks/sec)
- Push notifications via ntfy.sh
- Persistent notification tracking (no duplicate alerts)
- Multi-node support

### Setup

1. **Install dependencies:**
```bash
pip install requests
```

2. **Configure nodes:**
```bash
cp config/example.json config/nodes.json
```

Edit `config/nodes.json`:
```json
{
  "ntfy_topic": "your-ntfy-topic",
  "nodes": {
    "node-name": {
      "url": "http://node-url:9944",
      "notified": false
    }
  }
}
```

3. **Run the monitor:**
```bash
python substrate_sync_monitor.py
```

### Configuration

- **ntfy_topic**: Your ntfy.sh topic for notifications
- **url**: Node RPC endpoint
- **notified**: Auto-updated when notification is sent (prevents duplicates)

### Output

The monitor displays:
- Current block / Target block
- Sync status and peer count
- ETA to full sync
- Sync progress percentage
- Blocks remaining
- Latest synced block age
- Sync rate (blocks/sec)
