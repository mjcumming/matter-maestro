from flask import Blueprint, jsonify, request
from ..logger import get_logger
from ..database.database import initialize_db, get_table

groups_blueprint = Blueprint('groups', __name__)
logger = get_logger(__name__)
db = initialize_db()
groups_table = get_table(db, 'groups')

@groups_blueprint.route('', methods=['GET'])
def get_groups():
    """
    Get all groups
    ---
    responses:
      200:
        description: List of all groups
    """
    groups = groups_table.all()
    return jsonify(groups)

@groups_blueprint.route('', methods=['POST'])
def create_group():
    """
    Create a new group
    ---
    parameters:
      - name: group
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            devices:
              type: array
              items:
                type: integer
    responses:
      201:
        description: Group created successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['name', 'devices']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        group_id = groups_table.insert(data)
        return jsonify({'id': group_id, **data}), 201
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return jsonify({'error': 'Failed to create group'}), 500

@groups_blueprint.route('/<int:group_id>/devices', methods=['POST'])
def add_device_to_group(group_id):
    """
    Add device to group
    ---
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
      - name: device
        in: body
        required: true
        schema:
          type: object
          properties:
            device_id:
              type: integer
    responses:
      200:
        description: Device added to group successfully
      404:
        description: Group not found
    """
    try:
        data = request.get_json()
        group = groups_table.get(doc_id=group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        devices = group.get('devices', [])
        devices.append(data['device_id'])
        groups_table.update({'devices': devices}, doc_ids=[group_id])
        
        return jsonify({'message': 'Device added to group successfully'})
    except Exception as e:
        logger.error(f"Error adding device to group: {e}")
        return jsonify({'error': 'Failed to add device to group'}), 500
