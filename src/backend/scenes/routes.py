from flask import Blueprint, jsonify, request
from ..logger import get_logger
from ..database.database import initialize_db, get_table

scenes_blueprint = Blueprint('scenes', __name__)
logger = get_logger(__name__)
db = initialize_db()
scenes_table = get_table(db, 'scenes')

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
                    type: integer
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
        scenes_table.update(data, doc_ids=[scene_id])
        return jsonify({'message': 'Scene updated successfully'})
    except Exception as e:
        logger.error(f"Error updating scene: {e}")
        return jsonify({'error': 'Scene not found'}), 404
