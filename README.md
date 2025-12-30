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

#### Option 1: Docker (Recommended)

1. **Configure nodes:**
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

3. **Run with Docker:**
```bash
docker run -v "$(pwd)/config:/app/config" glokos/substrate-sync-status:latest
```

#### Option 2: Local Python

1. **Install dependencies:**
```bash
pip install requests
```

2. **Configure nodes** (same as above)

3. **Run the monitor:**
```bash
python substrate_sync_monitor.py
```

### Docker Notes

- Multi-architecture support: amd64, arm64 (M1/M2 Macs, Raspberry Pi 3/4/5), arm/v7 (Raspberry Pi 2/3)
- For Tailscale networks: use IP addresses instead of hostnames in `config/nodes.json`
- On macOS with Tailscale: add `--add-host=host.docker.internal:host-gateway` flag

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
