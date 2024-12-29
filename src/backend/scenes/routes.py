from flask import Blueprint, jsonify, request, render_template
from ..logger import get_logger
from ..database.database import initialize_db, get_table
from ..matter.protocol_manager import protocol_manager

scenes_blueprint = Blueprint('scenes', __name__)
logger = get_logger(__name__)
db = initialize_db()
scenes_table = get_table(db, 'scenes')

@scenes_blueprint.route('/ui', methods=['GET'])
def scenes_ui():
    """Render the scenes management UI"""
    return render_template('scenes.html')

@scenes_blueprint.route('', methods=['GET'])
def get_scenes():
    """
    Get all scenes
    ---
    responses:
      200:
        description: List of all scenes
    """
    scenes = scenes_table.all()
    return jsonify(scenes)

@scenes_blueprint.route('/<int:scene_id>', methods=['GET'])
def get_scene(scene_id):
    """
    Get a specific scene
    ---
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene details
      404:
        description: Scene not found
    """
    scene = scenes_table.get(doc_id=scene_id)
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    return jsonify(scene)

@scenes_blueprint.route('', methods=['POST'])
def create_scene():
    """
    Create a new scene
    ---
    parameters:
      - name: scene
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
                type: object
                properties:
                  device_id:
                    type: string
                  state:
                    type: object
    responses:
      201:
        description: Scene created successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['name', 'devices']):
            return jsonify({'error': 'Missing required fields'}), 400

        scene_id = scenes_table.insert(data)
        return jsonify({'id': scene_id, **data}), 201
    except Exception as e:
        logger.error(f"Error creating scene: {e}")
        return jsonify({'error': 'Failed to create scene'}), 500

@scenes_blueprint.route('/<int:scene_id>/activate', methods=['POST'])
async def activate_scene(scene_id):
    """
    Activate a scene
    ---
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene activated successfully
      404:
        description: Scene not found
      500:
        description: Error activating scene
    """
    try:
        scene = scenes_table.get(doc_id=scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        # Initialize Matter protocol if needed
        await protocol_manager.initialize()

        # Apply scene state to each device
        for device in scene['devices']:
            try:
                await protocol_manager.control_device(
                    node_id=device['device_id'],
                    command='apply_state',
                    params=device['state']
                )
            except Exception as e:
                logger.error(f"Error applying scene state to device {device['device_id']}: {e}")
                continue

        return jsonify({'message': 'Scene activated successfully'})
    except Exception as e:
        logger.error(f"Error activating scene: {e}")
        return jsonify({'error': 'Failed to activate scene'}), 500

@scenes_blueprint.route('/<int:scene_id>', methods=['PUT'])
def update_scene(scene_id):
    """
    Update a scene
    ---
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
      - name: scene
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
                type: object
    responses:
      200:
        description: Scene updated successfully
      404:
        description: Scene not found
    """
    try:
        data = request.get_json()
        if not scenes_table.get(doc_id=scene_id):
            return jsonify({'error': 'Scene not found'}), 404

        scenes_table.update(data, doc_ids=[scene_id])
        return jsonify({'message': 'Scene updated successfully'})
    except Exception as e:
        logger.error(f"Error updating scene: {e}")
        return jsonify({'error': 'Scene not found'}), 404

@scenes_blueprint.route('/<int:scene_id>', methods=['DELETE'])
def delete_scene(scene_id):
    """
    Delete a scene
    ---
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene deleted successfully
      404:
        description: Scene not found
    """
    try:
        if not scenes_table.get(doc_id=scene_id):
            return jsonify({'error': 'Scene not found'}), 404

        scenes_table.remove(doc_ids=[scene_id])
        return jsonify({'message': 'Scene deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting scene: {e}")
        return jsonify({'error': 'Scene not found'}), 404