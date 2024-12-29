from flask import Blueprint, jsonify, request
from ..logger import get_logger
from ..database.database import initialize_db, get_table

devices_blueprint = Blueprint('devices', __name__)
logger = get_logger(__name__)
db = initialize_db()
devices_table = get_table(db, 'devices')

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
