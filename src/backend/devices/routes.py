from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from ..logger import get_logger
from ..database.database import initialize_db, get_table
from ..matter.protocol_manager import protocol_manager
import asyncio

devices_blueprint = Blueprint('devices', __name__)
logger = get_logger(__name__)
db = initialize_db()
devices_table = get_table(db, 'devices')

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(f(*args, **kwargs))
            return result
        finally:
            loop.close()
    return wrapped

@devices_blueprint.route('', methods=['GET'])
def get_devices():
    """
    Get all devices
    ---
    responses:
      200:
        description: List of all devices
    """
    devices = devices_table.all()
    return jsonify(devices)

@devices_blueprint.route('', methods=['POST'])
def add_device():
    """
    Add a new device
    ---
    parameters:
      - name: device
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            type:
              type: string
            node_id:
              type: string
    responses:
      201:
        description: Device added successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['name', 'type', 'node_id']):
            return jsonify({'error': 'Missing required fields'}), 400

        device_id = devices_table.insert(data)
        return jsonify({'id': device_id, **data}), 201
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({'error': 'Failed to add device'}), 500

@devices_blueprint.route('/<int:device_id>', methods=['DELETE'])
def remove_device(device_id):
    """
    Remove a device
    ---
    parameters:
      - name: device_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Device removed successfully
      404:
        description: Device not found
    """
    try:
        devices_table.remove(doc_ids=[device_id])
        return jsonify({'message': 'Device removed successfully'})
    except Exception as e:
        logger.error(f"Error removing device: {e}")
        return jsonify({'error': 'Device not found'}), 404

@devices_blueprint.route('/discover', methods=['POST'])
@async_route
async def discover_devices():
    """
    Discover Matter devices in the network
    ---
    responses:
      200:
        description: List of discovered devices
      500:
        description: Error during device discovery
    """
    try:
        await protocol_manager.initialize()
        return jsonify({'message': 'Device discovery initiated'}), 200
    except Exception as e:
        logger.error(f"Error during device discovery: {e}")
        return jsonify({'error': 'Failed to discover devices'}), 500

@devices_blueprint.route('/<string:node_id>/control', methods=['POST'])
@async_route
async def control_device(node_id):
    """
    Control a Matter device
    ---
    parameters:
      - name: node_id
        in: path
        type: string
        required: true
      - name: command
        in: body
        required: true
        schema:
          type: object
          properties:
            command:
              type: string
            params:
              type: object
    responses:
      200:
        description: Command sent successfully
      404:
        description: Device not found
      500:
        description: Error controlling device
    """
    try:
        data = request.get_json()
        command = data.get('command')
        params = data.get('params', {})

        result = await protocol_manager.control_device(node_id, command, params)
        return jsonify({'result': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error controlling device: {e}")
        return jsonify({'error': 'Failed to control device'}), 500

@devices_blueprint.route('/<string:node_id>/info', methods=['GET'])
@async_route
async def get_device_info(node_id):
    """
    Get detailed information about a device
    ---
    parameters:
      - name: node_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Device information
      404:
        description: Device not found
    """
    try:
        info = await protocol_manager.get_node_info(node_id)
        if not info:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting device info: {e}")
        return jsonify({'error': 'Failed to get device information'}), 500