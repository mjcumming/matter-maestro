from functools import wraps
from flask import Blueprint, jsonify, request, current_app, render_template
from ..logger import get_logger
from ..database.database import initialize_db, get_table
from ..matter.protocol_manager import protocol_manager
import asyncio
from datetime import datetime

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

@devices_blueprint.route('/ui', methods=['GET'])
def devices_ui():
    """Render the devices management UI"""
    return render_template('devices.html')

@devices_blueprint.route('', methods=['GET'])
def get_devices():
    """
    Get all devices
    ---
    responses:
      200:
        description: List of all devices
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              type:
                type: string
              status:
                type: string
              last_seen:
                type: string
                format: date-time
    """
    devices = devices_table.all()
    for device in devices:
        device['online'] = True  # TODO: Implement real online status check
        device['last_seen'] = datetime.now().isoformat()
    return jsonify(devices)

@devices_blueprint.route('/pair', methods=['POST'])
@async_route
async def pair_device():
    """
    Pair a new Matter device
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            setup_code:
              type: string
              pattern: '[0-9]{8}'
              example: '12345678'
    responses:
      200:
        description: Device paired successfully
      400:
        description: Invalid setup code
    """
    try:
        data = request.get_json()
        setup_code = data.get('setup_code')

        if not setup_code or not setup_code.isdigit() or len(setup_code) != 8:
            return jsonify({'error': 'Invalid setup code'}), 400

        await protocol_manager.initialize()

        # TODO: Implement actual Matter pairing logic
        return jsonify({
            'message': 'Device paired successfully',
            'device_id': 'mock_id'
        })
    except Exception as e:
        logger.error(f"Error pairing device: {e}")
        return jsonify({'error': 'Failed to pair device'}), 500

@devices_blueprint.route('', methods=['POST'])
def add_device():
    """
    Add a new device
    ---
    parameters:
      - in: body
        name: body
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

@devices_blueprint.route('/discover', methods=['POST'])
@async_route
async def discover_devices():
    """
    Discover Matter devices in the network
    ---
    responses:
      200:
        description: List of discovered devices
        schema:
          type: object
          properties:
            message:
              type: string
            devices:
              type: array
              items:
                type: object
      500:
        description: Error during device discovery
    """
    try:
        await protocol_manager.initialize()
        devices = await protocol_manager._discover_nodes()
        return jsonify({'message': 'Device discovery completed', 'devices': devices})
    except Exception as e:
        logger.error(f"Error during device discovery: {e}")
        return jsonify({'error': 'Failed to discover devices'}), 500

@devices_blueprint.route('/<string:node_id>/info', methods=['GET'])
@async_route
async def get_device_info(node_id):
    """
    Get detailed information about a device
    ---
    parameters:
      - in: path
        name: node_id
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

@devices_blueprint.route('/<string:node_id>/control', methods=['POST'])
@async_route
async def control_device(node_id):
    """
    Control a Matter device
    ---
    parameters:
      - in: path
        name: node_id
        type: string
        required: true
      - in: body
        name: body
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
    """
    try:
        data = request.get_json()
        command = data.get('command')
        params = data.get('params', {})

        result = await protocol_manager.control_device(node_id, command, params)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error controlling device: {e}")
        return jsonify({'error': 'Failed to control device'}), 500

@devices_blueprint.route('/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """
    Delete a device from the system
    ---
    parameters:
      - in: path
        name: device_id
        type: string
        required: true
    responses:
      200:
        description: Device deleted successfully
      404:
        description: Device not found
    """
    try:
        devices_table.remove(doc_ids=[device_id])
        return jsonify({'message': 'Device deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return jsonify({'error': 'Device not found'}), 404

@devices_blueprint.route('/<string:device_id>/fabrics', methods=['GET'])
@async_route
async def get_device_fabrics(device_id):
    """
    Get all fabrics a device is connected to
    ---
    parameters:
      - in: path
        name: device_id
        type: string
        required: true
    responses:
      200:
        description: List of fabrics the device is connected to
        schema:
          type: object
          properties:
            fabrics:
              type: array
              items:
                type: object
                properties:
                  fabric_id:
                    type: string
                  name:
                    type: string
                  is_primary:
                    type: boolean
      404:
        description: Device not found
    """
    try:
        await protocol_manager.initialize()
        device = devices_table.get(doc_id=device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404

        # Get fabric information from the Matter protocol manager
        fabrics = await protocol_manager.get_device_fabrics(device_id)
        return jsonify({'fabrics': fabrics})
    except Exception as e:
        logger.error(f"Error getting device fabrics: {e}")
        return jsonify({'error': 'Failed to get device fabrics'}), 500