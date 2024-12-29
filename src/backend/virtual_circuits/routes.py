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
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              type:
                type: string
                enum: [switch, dimmer, color]
              devices:
                type: array
                items:
                  type: object
                  properties:
                    device_id:
                      type: integer
                    role:
                      type: string
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
            type:
              type: string
              enum: [switch, dimmer, color]
            devices:
              type: array
              items:
                type: object
                properties:
                  device_id:
                    type: integer
                  role:
                    type: string
                    enum: [primary, secondary]
    responses:
      201:
        description: Circuit created successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['name', 'type', 'devices']):
            return jsonify({'error': 'Missing required fields'}), 400

        if data['type'] not in ['switch', 'dimmer', 'color']:
            return jsonify({'error': 'Invalid circuit type'}), 400

        # Register with virtual circuit manager
        circuit_data = circuit_manager.register_circuit(data)

        # Save to database
        circuit_id = circuits_table.insert(circuit_data)
        return jsonify({'id': circuit_id, **circuit_data}), 201
    except Exception as e:
        logger.error(f"Error creating virtual circuit: {e}")
        return jsonify({'error': str(e)}), 500

@virtual_circuits_blueprint.route('/<int:circuit_id>', methods=['GET'])
def get_circuit(circuit_id):
    """
    Get a specific virtual circuit
    ---
    parameters:
      - name: circuit_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Circuit details
      404:
        description: Circuit not found
    """
    try:
        circuit = circuit_manager.get_circuit(circuit_id)
        if not circuit:
            return jsonify({'error': 'Circuit not found'}), 404
        return jsonify(circuit)
    except Exception as e:
        logger.error(f"Error getting circuit: {e}")
        return jsonify({'error': 'Circuit not found'}), 404

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
        circuit_manager.delete_circuit(circuit_id)
        circuits_table.remove(doc_ids=[circuit_id])
        return jsonify({'message': 'Circuit deleted successfully'})
    except ValueError as e:
        logger.error(f"Error deleting circuit: {e}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting circuit: {e}")
        return jsonify({'error': 'Failed to delete circuit'}), 500

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
              properties:
                on:
                  type: boolean
                brightness:
                  type: integer
                  minimum: 0
                  maximum: 100
                hue:
                  type: integer
                  minimum: 0
                  maximum: 360
                saturation:
                  type: integer
                  minimum: 0
                  maximum: 100
                value:
                  type: integer
                  minimum: 0
                  maximum: 100
    responses:
      200:
        description: Circuit triggered successfully
      404:
        description: Circuit not found
      400:
        description: Invalid state for circuit type
    """
    try:
        data = request.get_json()
        circuit = circuit_manager.get_circuit(circuit_id)
        if not circuit:
            return jsonify({'error': 'Circuit not found'}), 404

        circuit_manager.trigger_circuit(circuit_id, data)
        return jsonify({'message': 'Circuit triggered successfully'})
    except ValueError as e:
        logger.error(f"Error triggering circuit: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error triggering circuit: {e}")
        return jsonify({'error': 'Failed to trigger circuit'}), 500