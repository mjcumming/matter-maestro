from flask import Blueprint, jsonify
from ..logger import get_logger
from .credential_manager import CredentialManager

credentials_blueprint = Blueprint('credentials', __name__)
logger = get_logger(__name__)
credential_manager = CredentialManager()

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
