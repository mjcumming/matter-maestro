"""Routes for backup management interface."""
from flask import Blueprint, jsonify, request, render_template
from ..logger import get_logger
from .manager import backup_manager

backup_blueprint = Blueprint('backup', __name__)
logger = get_logger(__name__)

@backup_blueprint.route('/ui', methods=['GET'])
def backup_ui():
    """Render the backup management UI."""
    return render_template('backup.html')

@backup_blueprint.route('/config', methods=['GET'])
def get_backup_config():
    """Get current backup configuration."""
    return jsonify(backup_manager.get_config())

@backup_blueprint.route('/config', methods=['POST'])
def update_backup_config():
    """Update backup configuration."""
    try:
        config = request.get_json()
        updated_config = backup_manager.update_config(config)
        return jsonify(updated_config)
    except Exception as e:
        logger.error(f"Error updating backup config: {e}")
        return jsonify({'error': str(e)}), 400

@backup_blueprint.route('/authenticate', methods=['POST'])
async def authenticate_service():
    """Authenticate with a cloud service."""
    try:
        data = request.get_json()
        service = data.get('service')
        credentials = data.get('credentials')
        
        if not service or not credentials:
            return jsonify({'error': 'Missing service or credentials'}), 400
            
        success = await backup_manager.authenticate_service(service, credentials)
        if success:
            return jsonify({'message': 'Authentication successful'})
        return jsonify({'error': 'Authentication failed'}), 401
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return jsonify({'error': str(e)}), 500

@backup_blueprint.route('/backup', methods=['POST'])
async def trigger_backup():
    """Trigger a manual backup."""
    try:
        result = await backup_manager.perform_backup(manual=True)
        if result['success']:
            return jsonify(result)
        return jsonify(result), 500
    except Exception as e:
        logger.error(f"Error triggering backup: {e}")
        return jsonify({'error': str(e)}), 500

@backup_blueprint.route('/restore/<backup_id>', methods=['POST'])
async def restore_backup(backup_id):
    """Restore from a specific backup."""
    try:
        result = await backup_manager.restore_backup(backup_id)
        if result['success']:
            return jsonify(result)
        return jsonify(result), 500
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return jsonify({'error': str(e)}), 500
