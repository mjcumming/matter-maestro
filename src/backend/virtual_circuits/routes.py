from flask import Blueprint, jsonify, request, render_template
from ..logger import get_logger
from ..database.database import initialize_db, get_table
from .virtual_manager import VirtualCircuitManager

virtual_circuits_blueprint = Blueprint('virtual_circuits', __name__)
logger = get_logger(__name__)
db = initialize_db()
circuits_table = get_table(db, 'virtual_circuits')
circuit_manager = VirtualCircuitManager()

@virtual_circuits_blueprint.route('/ui', methods=['GET'])
def virtual_circuits_ui():
    """
    Render the virtual circuits UI
    """
    return render_template('virtual_circuits.html')

@virtual_circuits_blueprint.route('', methods=['GET'])
def get_circuits():
    """
    Get all virtual circuits
    ---
    responses:
      200:
        description: List of all virtual circuits
    """
    circuits = circuits_table.all()
    return jsonify(circuits)

@virtual_circuits_blueprint.route('', methods=['POST'])
def create_circuit():
    """
    Create a new virtual circuit
    ---
    parameters:
      - name: circuit
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
                  role:
                    type: string
    responses:
      201:
        description: Circuit created successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['name', 'devices']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Register with virtual circuit manager
        circuit_manager.register_circuit(data)

        circuit_id = circuits_table.insert(data)
        return jsonify({'id': circuit_id, **data}), 201
    except Exception as e:
        logger.error(f"Error creating virtual circuit: {e}")
        return jsonify({'error': 'Failed to create virtual circuit'}), 500

@virtual_circuits_blueprint.route('/<int:circuit_id>', methods=['DELETE'])
def delete_circuit(circuit_id):
    """
    Delete a virtual circuit
    ---
    parameters:
      - name: circuit_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Circuit deleted successfully
      404:
        description: Circuit not found
    """
    try:
        circuits_table.remove(doc_ids=[circuit_id])
        return jsonify({'message': 'Circuit deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting circuit: {e}")
        return jsonify({'error': 'Circuit not found'}), 404

@virtual_circuits_blueprint.route('/<int:circuit_id>/trigger', methods=['POST'])
def trigger_circuit(circuit_id):
    """
    Trigger a virtual circuit
    ---
    parameters:
      - name: circuit_id
        in: path
        type: integer
        required: true
      - name: trigger
        in: body
        required: true
        schema:
          type: object
          properties:
            device_id:
              type: integer
            state:
              type: object
    responses:
      200:
        description: Circuit triggered successfully
      404:
        description: Circuit not found
    """
    try:
        data = request.get_json()
        circuit = circuits_table.get(doc_id=circuit_id)
        if not circuit:
            return jsonify({'error': 'Circuit not found'}), 404

        circuit_manager.trigger_circuit(circuit_id, data)
        return jsonify({'message': 'Circuit triggered successfully'})
    except Exception as e:
        logger.error(f"Error triggering circuit: {e}")
        return jsonify({'error': 'Failed to trigger circuit'}), 500