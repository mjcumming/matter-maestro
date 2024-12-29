from ..logger import get_logger

logger = get_logger(__name__)

class VirtualCircuitManager:
    def __init__(self):
        self.circuits = {}
        self.device_mappings = {}

    def register_circuit(self, circuit_data):
        """Register a new virtual circuit."""
        circuit_id = circuit_data.get('id')
        circuit_type = circuit_data.get('type', 'switch')  # Default to switch type

        # Validate circuit type
        if circuit_type not in ['switch', 'dimmer', 'color']:
            raise ValueError(f"Invalid circuit type: {circuit_type}")

        self.circuits[circuit_id] = {
            **circuit_data,
            'type': circuit_type,
            'name': circuit_data.get('name', f'Circuit {circuit_id}')
        }

        # Map devices to circuits for quick lookup
        for device in circuit_data.get('devices', []):
            device_id = device.get('device_id')
            if device_id not in self.device_mappings:
                self.device_mappings[device_id] = []
            self.device_mappings[device_id].append(circuit_id)

        logger.info(f"Registered virtual circuit: {circuit_id} ({circuit_type})")
        return self.circuits[circuit_id]

    def get_circuit(self, circuit_id):
        """Get circuit details by ID."""
        return self.circuits.get(circuit_id)

    def delete_circuit(self, circuit_id):
        """Delete a virtual circuit and clean up mappings."""
        if circuit_id not in self.circuits:
            raise ValueError(f"Circuit {circuit_id} not found")

        # Remove device mappings
        circuit = self.circuits[circuit_id]
        for device in circuit.get('devices', []):
            device_id = device.get('device_id')
            if device_id in self.device_mappings:
                self.device_mappings[device_id].remove(circuit_id)
                if not self.device_mappings[device_id]:
                    del self.device_mappings[device_id]

        # Remove circuit
        del self.circuits[circuit_id]
        logger.info(f"Deleted virtual circuit: {circuit_id}")

    def trigger_circuit(self, circuit_id, trigger_data):
        """Trigger a virtual circuit and update linked devices."""
        try:
            circuit = self.circuits.get(circuit_id)
            if not circuit:
                raise ValueError(f"Circuit {circuit_id} not found")

            trigger_device = trigger_data.get('device_id')
            new_state = trigger_data.get('state')
            circuit_type = circuit.get('type', 'switch')

            # Validate state based on circuit type
            if circuit_type == 'switch' and not isinstance(new_state.get('on'), bool):
                raise ValueError("Switch state must include boolean 'on' value")
            elif circuit_type == 'dimmer' and not isinstance(new_state.get('brightness'), (int, float)):
                raise ValueError("Dimmer state must include 'brightness' value")
            elif circuit_type == 'color' and not all(k in new_state for k in ['hue', 'saturation', 'value']):
                raise ValueError("Color state must include 'hue', 'saturation', and 'value'")

            # Update state for all linked devices
            for device in circuit.get('devices', []):
                if device.get('device_id') != trigger_device:
                    self._update_device_state(device.get('device_id'), new_state, circuit_type)

            logger.info(f"Triggered circuit {circuit_id} ({circuit_type}) from device {trigger_device}")
        except Exception as e:
            logger.error(f"Error triggering circuit: {e}")
            raise

    def _update_device_state(self, device_id, state, circuit_type):
        """Update the state of a device based on circuit type."""
        logger.info(f"Updating device {device_id} state to {state} (type: {circuit_type})")
        # TODO: Implement actual Matter device state update based on circuit type
        pass