import time
import requests
import logging

# Configuration
NODES = {
    "mainnet-doc": "http://mainnet-doc:9944",
}
NTFY_TOPIC = "abumaherdevops"
CHECK_INTERVAL = 30  # seconds
SYNCED_NODES = {node: False for node in NODES}  # Tracks sync status
node_block_history = {}  # Stores previous block height and timestamp

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m - \033[1;32m%(levelname)s\033[0m - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SyncChecker")


def get_sync_status(node_identifier, url):
    """Query a Substrate node for its sync status."""
    payload = {"jsonrpc": "2.0", "method": "system_syncState", "params": [], "id": 1}
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json().get("result", {})
        return data.get("currentBlock"), data.get("highestBlock")
    except requests.RequestException as e:
        logger.error("🚨 [%s] Failed to fetch sync status: %s", node_identifier, e)
        return None, None


def calculate_eta(node_identifier, current_block_number, target_block_number):
    """Calculate ETA for full sync based on sync speed."""
    global node_block_history

    if node_identifier in node_block_history:
        previous_block_number, previous_measurement_timestamp = node_block_history[
            node_identifier
        ]
        time_elapsed = time.time() - previous_measurement_timestamp
        sync_speed = (
            (current_block_number - previous_block_number) / time_elapsed
            if time_elapsed > 0
            else 0
        )
    else:
        sync_speed = None  # First measurement, no previous data

    # Update previous block state
    node_block_history[node_identifier] = (current_block_number, time.time())

    if sync_speed and sync_speed > 0:
        remaining_blocks_to_sync = target_block_number - current_block_number
        eta_seconds = remaining_blocks_to_sync / sync_speed

        # Convert to human-readable time
        days = int(eta_seconds // 86400)
        hours = int((eta_seconds % 86400) // 3600)
        minutes = int((eta_seconds % 3600) // 60)

        if days > 0:
            return f"⏳ {days}d {hours}h {minutes}m remaining"
        elif hours > 0:
            return f"⏳ {hours}h {minutes}m remaining"
        else:
            return f"⏳ {minutes}m remaining"
    else:
        return "⏳ Calculating..."


def send_ntfy_notification(node_identifier):
    """Send a notification when a node gets fully synced."""
    message = f"✅ {node_identifier} is now fully synced! 🎉🚀"
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"), timeout=5
        )
        logger.info("📢 [%s] Sent notification: %s", node_identifier, message)
    except requests.RequestException as e:
        logger.error("⚠️ [%s] Failed to send notification: %s", node_identifier, e)


def format_time_duration(total_seconds):
    """Convert total seconds into a human-readable time duration."""
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def calculate_sync_rate(node_identifier, current_block_number, target_block_number):
    """Calculate sync rate in blocks per second."""
    global node_block_history

    if node_identifier in node_block_history:
        previous_block_number, previous_measurement_timestamp = node_block_history[
            node_identifier
        ]
        time_elapsed = time.time() - previous_measurement_timestamp

        if time_elapsed > 0:
            blocks_synced_per_second = (
                current_block_number - previous_block_number
            ) / time_elapsed
            return f"{blocks_synced_per_second:.2f} blocks/sec"

    return "Calculating..."


def check_nodes():
    """Check the sync status of all nodes and send notifications if needed."""
    for node_identifier, node_rpc_endpoint in NODES.items():
        current_block_number, target_block_number = get_sync_status(
            node_identifier, node_rpc_endpoint
        )
        if (
            current_block_number is None
            or target_block_number is None
            or target_block_number == 0
        ):
            continue  # Skip if there was an error fetching data or divide-by-zero risk

        is_node_synced = (
            current_block_number >= target_block_number - 1
        )  # Allow slight lag
        estimated_time_to_sync = calculate_eta(
            node_identifier, current_block_number, target_block_number
        )

        sync_progress_percentage = (current_block_number / target_block_number) * 100
        sync_progress_str = f"{sync_progress_percentage:.2f}%"
        remaining_blocks_to_sync = target_block_number - current_block_number

        # Convert block age to seconds (assuming 6 seconds per block)
        block_age_seconds = remaining_blocks_to_sync * 6
        block_age_str = format_time_duration(block_age_seconds)

        # Calculate sync rate
        sync_rate = calculate_sync_rate(
            node_identifier, current_block_number, target_block_number
        )

        logger.info(
            "🔄 [%s] Current: %s | Target: %s | Synced: %s | ETA: %s | Progress: %s | Blocks Left: %s | Latest Synced Block Age: %s | Sync Rate: %s",
            node_identifier,
            current_block_number,
            target_block_number,
            is_node_synced,
            estimated_time_to_sync,
            sync_progress_str,
            remaining_blocks_to_sync,
            block_age_str,
            sync_rate,
        )

        # Send notification only when transitioning to a synced state
        if is_node_synced and not SYNCED_NODES[node_identifier]:
            send_ntfy_notification(node_identifier)

        # Update previous block state
        node_block_history[node_identifier] = (current_block_number, time.time())

        # Update sync status
        SYNCED_NODES[node_identifier] = is_node_synced


if __name__ == "__main__":
    logger.info("🚀 Starting sync checker ...")
    while True:
        check_nodes()
        logger.info("⏳ Sleeping for %s seconds...", CHECK_INTERVAL)
        time.sleep(CHECK_INTERVAL)
