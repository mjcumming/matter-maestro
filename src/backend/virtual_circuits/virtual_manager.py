from ..logger import get_logger

logger = get_logger(__name__)

class VirtualCircuitManager:
    def __init__(self):
        self.circuits = {}
        self.device_mappings = {}
    
    def register_circuit(self, circuit_data):
        """Register a new virtual circuit."""
        circuit_id = circuit_data.get('id')
        self.circuits[circuit_id] = circuit_data
        
        # Map devices to circuits for quick lookup
        for device in circuit_data.get('devices', []):
            device_id = device.get('device_id')
            if device_id not in self.device_mappings:
                self.device_mappings[device_id] = []
            self.device_mappings[device_id].append(circuit_id)
        
        logger.info(f"Registered virtual circuit: {circuit_id}")
    
    def trigger_circuit(self, circuit_id, trigger_data):
        """Trigger a virtual circuit and update linked devices."""
        try:
            circuit = self.circuits.get(circuit_id)
            if not circuit:
                raise ValueError(f"Circuit {circuit_id} not found")
            
            trigger_device = trigger_data.get('device_id')
            new_state = trigger_data.get('state')
            
            # Update state for all linked devices
            for device in circuit.get('devices', []):
                if device.get('device_id') != trigger_device:
                    self._update_device_state(device.get('device_id'), new_state)
            
            logger.info(f"Triggered circuit {circuit_id} from device {trigger_device}")
        except Exception as e:
            logger.error(f"Error triggering circuit: {e}")
            raise
    
    def _update_device_state(self, device_id, state):
        """Update the state of a device (to be implemented with actual Matter device control)."""
        logger.info(f"Updating device {device_id} state to {state}")
        # TODO: Implement actual Matter device state update
        pass
