import re
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
            operational_credentials:
              type: object
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
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            fabric_id:
              type: string
              pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
            vendor_id:
              type: string
              pattern: '^0x[0-9a-fA-F]{4}$'
    responses:
      200:
        description: Credentials initialized successfully
      400:
        description: Invalid credentials format
      500:
        description: Error initializing credentials
    """
    try:
        data = request.get_json()
        fabric_id = data.get('fabric_id')
        vendor_id = data.get('vendor_id')

        if not fabric_id or not vendor_id:
            return jsonify({'error': 'Both fabric_id and vendor_id are required'}), 400

        # Validate fabric_id format (UUID v4)
        if not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$', fabric_id):
            return jsonify({'error': 'Invalid fabric_id format'}), 400

        # Validate vendor_id format (0xXXXX)
        if not re.match(r'^0x[0-9a-fA-F]{4}$', vendor_id):
            return jsonify({'error': 'Invalid vendor_id format'}), 400

        logger.info(f"Initializing new fabric credentials with ID: {fabric_id} and vendor ID: {vendor_id}")
        result = credential_manager.initialize_new_credentials(fabric_id=fabric_id, vendor_id=vendor_id)

        if result:
            logger.info("Successfully initialized new credentials")
            return jsonify({'message': 'Credentials initialized successfully'})

        logger.error("Failed to initialize credentials")
        return jsonify({'error': 'Failed to initialize credentials'}), 500
    except Exception as e:
        logger.error(f"Error initializing credentials: {e}")
        return jsonify({'error': str(e)}), 500

@credentials_blueprint.route('/delete', methods=['POST'])
def delete_credentials():
    """
    Delete current Matter fabric credentials
    ---
    responses:
      200:
        description: Credentials deleted successfully
      500:
        description: Error deleting credentials
    """
    try:
        logger.info("Deleting fabric credentials")
        result = credential_manager.delete_credentials()
        if result:
            logger.info("Successfully deleted credentials")
            return jsonify({'message': 'Credentials deleted successfully'})
        logger.error("Failed to delete credentials")
        return jsonify({'error': 'Failed to delete credentials'}), 500
    except Exception as e:
        logger.error(f"Error deleting credentials: {e}")
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
              pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    responses:
      200:
        description: Fabric ID updated successfully
      400:
        description: Invalid fabric ID format
      500:
        description: Error updating fabric ID
    """
    try:
        data = request.get_json()
        new_fabric_id = data.get('fabric_id')

        if not new_fabric_id:
            return jsonify({'error': 'Fabric ID is required'}), 400

        # Validate fabric_id format (UUID v4)
        if not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$', new_fabric_id):
            return jsonify({'error': 'Invalid fabric_id format'}), 400

        if credential_manager.update_fabric_id(new_fabric_id):
            return jsonify({'message': 'Fabric ID updated successfully'})
        return jsonify({'error': 'Failed to update fabric ID'}), 500
    except Exception as e:
        logger.error(f"Error updating fabric ID: {e}")
        return jsonify({'error': str(e)}), 500