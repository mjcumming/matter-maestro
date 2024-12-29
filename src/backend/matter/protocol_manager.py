"""Matter Protocol Manager for handling device communication and fabric management."""
import asyncio
from matter_server.client import MatterClient
from ..logger import get_logger

logger = get_logger(__name__)

class MatterProtocolManager:
    def __init__(self):
        self.client = None
        self._nodes = {}
        self._initialized = False

    async def initialize(self):
        """Initialize Matter client and start fabric management."""
        if self._initialized:
            return

        try:
            # Connect to Matter server
            self.client = await MatterClient.create(
                host="localhost",
                port=5580,  # Default Matter server port
            )
            logger.info("Successfully connected to Matter server")
            self._initialized = True

            # Start node discovery
            await self._discover_nodes()
        except Exception as e:
            logger.error(f"Failed to initialize Matter client: {e}")
            self._initialized = False
            raise

    async def _discover_nodes(self):
        """Discover Matter nodes in the network."""
        if not self._initialized:
            await self.initialize()

        try:
            nodes = await self.client.get_nodes()
            self._nodes.clear()

            for node in nodes:
                node_id = str(node['node_id'])
                self._nodes[node_id] = {
                    'node_id': node_id,
                    'device_type': node.get('device_type', 'unknown'),
                    'endpoints': node.get('endpoints', [])
                }
                logger.info(f"Discovered node: {node_id}")

            return list(self._nodes.values())
        except Exception as e:
            logger.error(f"Error discovering nodes: {e}")
            return []

    async def get_node_info(self, node_id: str) -> dict:
        """Get information about a specific node."""
        if not self._initialized:
            await self.initialize()

        try:
            node = self._nodes.get(node_id)
            return node if node else {}
        except Exception as e:
            logger.error(f"Error getting node info: {e}")
            return {}

    async def control_device(self, node_id: str, command: str, params: dict = None) -> dict:
        """Send control command to a device."""
        if not self._initialized:
            await self.initialize()

        try:
            if node_id not in self._nodes:
                raise ValueError(f"Node {node_id} not found")

            # Execute command through the Matter client
            result = await self.client.send_command(
                node_id=node_id,
                command=command,
                parameters=params or {}
            )
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"Error controlling device {node_id}: {e}")
            return {'success': False, 'error': str(e)}

# Create a singleton instance
protocol_manager = MatterProtocolManager()