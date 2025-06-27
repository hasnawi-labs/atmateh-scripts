import time
import requests
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static
from typing import Dict, Optional, Tuple, Any

# Configuration (move to a config file later)
NODES: Dict[str, str] = {
    "mainnet-doc": "http://mainnet-doc:9944",
    "mainnet-dopey": "http://mainnet-dopey:9944",
}


class NodeSyncMonitor(Screen):
    """Main screen for monitoring node synchronization."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the screen with block history tracking."""
        super().__init__(*args, **kwargs)
        # Track block history for each node
        self.node_block_history: Dict[str, Tuple[int, float]] = {}

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        yield Container(DataTable(id="node_stats"), Static(id="sync_summary"))
        yield Footer()

    def on_mount(self) -> None:
        """Set up the initial state when the screen mounts."""
        # Configure the data table
        node_stats_table = self.query_one("#node_stats", DataTable)
        node_stats_table.add_columns(
            "Node",
            "Current Block",
            "Target Block",
            "Sync %",
            "Blocks Left",
            "Sync Rate",
            "ETA",
            "Latest Block Age",
        )

        # Start periodic updates
        self.set_interval(5, self.update_node_stats)

    def get_sync_status(
        self, node_name: str, url: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """Fetch synchronization status for a given Substrate node."""
        try:
            # Substrate RPC payload to get sync state
            payload = {
                "jsonrpc": "2.0",
                "method": "system_syncState",
                "params": [],
                "id": 1,
            }

            # Send POST request to the node's RPC endpoint
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()

            # Parse the response
            result = response.json().get("result", {})
            current_block = result.get("currentBlock")
            highest_block = result.get("highestBlock")

            return current_block, highest_block
        except Exception as e:
            print(f"Error fetching sync status for {node_name}: {e}")
            return None, None

    def calculate_sync_rate(self, node_name: str, current_block: int) -> str:
        """Calculate synchronization rate for a node."""
        current_time = time.time()

        # Check if we have a previous block measurement
        if node_name in self.node_block_history:
            previous_block, previous_time = self.node_block_history[node_name]
            time_elapsed = current_time - previous_time

            # Calculate blocks per second
            if time_elapsed > 0:
                sync_rate = (current_block - previous_block) / time_elapsed
                return f"{sync_rate:.2f} blocks/sec"

        # Update block history for next iteration
        self.node_block_history[node_name] = (current_block, current_time)

        return "Calculating..."

    def format_time_duration(self, total_seconds: int) -> str:
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

    def calculate_eta(self, current_block: int, highest_block: int) -> str:
        """Calculate estimated time to full synchronization."""
        blocks_left = highest_block - current_block
        # Assuming 6 seconds per block
        total_seconds = blocks_left * 6

        # If sync is complete or near complete
        if blocks_left <= 1:
            return "Synced ✓"

        return f"{self.format_time_duration(total_seconds)}"

    def calculate_block_age(self, current_block: int, highest_block: int) -> str:
        """Calculate the age of the latest synced block."""
        blocks_left = highest_block - current_block
        # Assuming 6 seconds per block
        total_seconds = blocks_left * 6

        return f"{self.format_time_duration(total_seconds)}"

    def update_node_stats(self) -> None:
        """Update node synchronization statistics."""
        node_stats_table = self.query_one("#node_stats", DataTable)
        node_stats_table.clear()

        for node_name, url in NODES.items():
            current_block, highest_block = self.get_sync_status(node_name, url)

            if current_block is None or highest_block is None or highest_block == 0:
                continue

            # Calculate sync percentage
            sync_percentage = (current_block / highest_block) * 100
            blocks_left = highest_block - current_block

            # Calculate sync rate
            sync_rate = self.calculate_sync_rate(node_name, current_block)

            # Calculate ETA
            eta = self.calculate_eta(current_block, highest_block)

            # Calculate block age
            block_age = self.calculate_block_age(current_block, highest_block)

            # Add row to the table
            node_stats_table.add_row(
                node_name,
                str(current_block),
                str(highest_block),
                f"{sync_percentage:.2f}%",
                str(blocks_left),
                sync_rate,
                eta,
                block_age,
            )

        # Update sync summary
        sync_summary = self.query_one("#sync_summary", Static)
        sync_summary.update(f"\n\n\nLast updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")


class SubstrateSyncApp(App):
    """Main Textual application for Substrate node sync monitoring."""

    def on_mount(self) -> None:
        """Set the initial screen when the app starts."""
        self.push_screen(NodeSyncMonitor())


def main():
    """Run the Substrate Sync Monitoring TUI."""
    app = SubstrateSyncApp()
    app.run()


if __name__ == "__main__":
    main()
