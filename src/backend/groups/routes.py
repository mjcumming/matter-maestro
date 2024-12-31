from flask import Blueprint, jsonify, request, render_template
from ..logger import get_logger
from ..database.database import initialize_db, get_table
from ..matter.protocol_manager import protocol_manager

groups_blueprint = Blueprint('groups', __name__)
logger = get_logger(__name__)
db = initialize_db()
groups_table = get_table(db, 'groups')

@groups_blueprint.route('/ui', methods=['GET'])
def groups_ui():
    """Render the groups management UI."""
    return render_template('groups.html')

@groups_blueprint.route('', methods=['GET'])
def get_groups():
    """
    Get all groups
    ---
    responses:
      200:
        description: List of all groups
    """
    try:
        groups = groups_table.all()
        return jsonify(groups)
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        return jsonify({'error': 'Failed to fetch groups'}), 500

@groups_blueprint.route('/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """
    Get a specific group
    ---
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Group details
      404:
        description: Group not found
    """
    try:
        group = groups_table.get(doc_id=group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        return jsonify({**group, 'id': group_id})
    except Exception as e:
        logger.error(f"Error fetching group {group_id}: {e}")
        return jsonify({'error': 'Failed to fetch group'}), 500

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
            description:
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
        if not data.get('name'):
            return jsonify({'error': 'Group name is required'}), 400

        # Ensure devices is always a list
        data['devices'] = data.get('devices', [])

        # Add the group to the database
        group_id = groups_table.insert(data)

        logger.info(f"Created group: {data['name']} with ID: {group_id}")
        return jsonify({'id': group_id, **data}), 201
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return jsonify({'error': 'Failed to create group'}), 500

@groups_blueprint.route('/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """
    Update a group
    ---
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
      - name: group
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            devices:
              type: array
              items:
                type: integer
    responses:
      200:
        description: Group updated successfully
      404:
        description: Group not found
    """
    try:
        data = request.get_json()
        if not groups_table.get(doc_id=group_id):
            return jsonify({'error': 'Group not found'}), 404

        groups_table.update(data, doc_ids=[group_id])
        logger.info(f"Updated group {group_id}")
        return jsonify({'id': group_id, **data})
    except Exception as e:
        logger.error(f"Error updating group {group_id}: {e}")
        return jsonify({'error': 'Failed to update group'}), 500

@groups_blueprint.route('/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """
    Delete a group
    ---
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Group deleted successfully
      404:
        description: Group not found
    """
    try:
        if not groups_table.get(doc_id=group_id):
            return jsonify({'error': 'Group not found'}), 404

        groups_table.remove(doc_ids=[group_id])
        logger.info(f"Deleted group {group_id}")
        return jsonify({'message': 'Group deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting group {group_id}: {e}")
        return jsonify({'error': 'Failed to delete group'}), 500

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
        if data['device_id'] not in devices:
            devices.append(data['device_id'])
            groups_table.update({'devices': devices}, doc_ids=[group_id])
            logger.info(f"Added device {data['device_id']} to group {group_id}")

        return jsonify({'message': 'Device added to group successfully'})
    except Exception as e:
        logger.error(f"Error adding device to group: {e}")
        return jsonify({'error': 'Failed to add device to group'}), 500