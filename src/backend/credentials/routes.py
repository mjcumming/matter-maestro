from flask import Blueprint, jsonify, request, render_template
from ..logger import get_logger
from .credential_manager import CredentialManager

credentials_blueprint = Blueprint('credentials', __name__)
logger = get_logger(__name__)
credential_manager = CredentialManager()

@credentials_blueprint.route('/ui', methods=['GET'])
def credentials_ui():
    """Render the credentials management UI"""
    return render_template('credentials.html')

@credentials_blueprint.route('', methods=['GET'])
def get_credentials():
    """
    Retrieve Matter fabric credentials
    ---
    responses:
      200:
        description: Current fabric credentials
        schema:
          type: object
          properties:
            fabric_id:
              type: string
            vendor_id:
              type: string
      500:
        description: Error retrieving credentials
    """
    try:
        creds = credential_manager.load_credentials()
        return jsonify(creds)
    except Exception as e:
        logger.error(f"Error retrieving credentials: {e}")
        return jsonify({'error': 'Failed to retrieve credentials'}), 500

@credentials_blueprint.route('/initialize', methods=['POST'])
def initialize_credentials():
    """
    Initialize new Matter fabric credentials
    ---
    responses:
      200:
        description: Credentials initialized successfully
      500:
        description: Error initializing credentials
    """
    try:
        logger.info("Initializing new fabric credentials")
        # Remove async/await since we're using synchronous operations
        result = credential_manager.initialize_new_credentials()
        if result:
            logger.info("Successfully initialized new credentials")
            return jsonify({'message': 'Credentials initialized successfully'})
        logger.error("Failed to initialize credentials")
        return jsonify({'error': 'Failed to initialize credentials'}), 500
    except Exception as e:
        logger.error(f"Error initializing credentials: {e}")
        return jsonify({'error': str(e)}), 500

@credentials_blueprint.route('/fabric', methods=['PUT'])
def update_fabric_id():
    """
    Update fabric ID
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            fabric_id:
              type: string
    responses:
      200:
        description: Fabric ID updated successfully
      400:
        description: Invalid fabric ID
      500:
        description: Error updating fabric ID
    """
    try:
        data = request.get_json()
        new_fabric_id = data.get('fabric_id')

        if not new_fabric_id:
            return jsonify({'error': 'Fabric ID is required'}), 400

        if credential_manager.update_fabric_id(new_fabric_id):
            return jsonify({'message': 'Fabric ID updated successfully'})
        return jsonify({'error': 'Failed to update fabric ID'}), 500
    except Exception as e:
        logger.error(f"Error updating fabric ID: {e}")
        return jsonify({'error': 'Failed to update fabric ID'}), 500