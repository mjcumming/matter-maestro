from flask import Blueprint, jsonify
from ..logger import get_logger
import socket
import netifaces
import asyncio
from ..matter.protocol_manager import protocol_manager

network_blueprint = Blueprint('network', __name__)
logger = get_logger(__name__)

@network_blueprint.route('/ipv6-status', methods=['GET'])
def get_ipv6_status():
    """Get IPv6 status of the network."""
    try:
        # Check if any interface has an IPv6 address
        ipv6_enabled = False
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET6 in addrs:
                ipv6_enabled = True
                break

        return jsonify({
            'enabled': ipv6_enabled,
            'message': 'IPv6 is enabled' if ipv6_enabled else 'IPv6 is not enabled'
        })
    except Exception as e:
        logger.error(f"Error checking IPv6 status: {e}")
        return jsonify({
            'enabled': False,
            'message': 'Failed to check IPv6 status'
        })

@network_blueprint.route('/matter-routers', methods=['GET'])
async def get_matter_routers():
    """Get Matter routers on the network."""
    try:
        # Initialize protocol manager if needed
        await protocol_manager.initialize()
        
        # Get discovered nodes that are Matter routers
        nodes = await protocol_manager._discover_nodes()
        routers = [node for node in nodes if node.get('is_router', False)]

        return jsonify({
            'routers': routers,
            'message': f'Found {len(routers)} Matter router(s)'
        })
    except Exception as e:
        logger.error(f"Error discovering Matter routers: {e}")
        return jsonify({
            'routers': [],
            'message': 'Failed to discover Matter routers'
        })
