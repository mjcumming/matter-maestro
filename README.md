# Matter Maestro - Local-First Fabric Controller

A sophisticated local-first Matter fabric controller designed for comprehensive IoT device management in smart home environments. Matter Maestro provides advanced capabilities for device pairing, commissioning, and virtual circuit management.

## Features

- **Local-First Architecture**: Run your Matter fabric controller entirely on your local network
- **Device Management**:
  - Easy device pairing and commissioning
  - Real-time device status monitoring
  - Comprehensive device information display
  - Multi-fabric support per device
  
- **Virtual Circuit Management**:
  - Drag-and-drop circuit creation interface
  - Support for different device types:
    - On/Off switches
    - Dimmers
    - Color-capable devices
  - Flexible device linking and grouping
  - Automatic state synchronization

- **Fabric Management**:
  - View and manage fabric credentials
  - Monitor fabric connections
  - Multi-fabric device support

## Setup

1. **Prerequisites**:
   - Python 3.11+
   - Matter server running locally (default port: 5580)

2. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/matter-maestro.git
   cd matter-maestro

   # Install dependencies
   pip install -r requirements.txt

   # Start the application
   python -m src.backend.app
   ```

3. **Access**:
   - Open `http://localhost:5000` in your browser
   - The API documentation is available at `http://localhost:5000/api/docs`

## Architecture

Matter Maestro follows a modular architecture:

- **Backend**:
  - Flask-based REST API
  - Asynchronous Matter protocol integration
  - TinyDB for local data storage
  - Modular blueprint structure for different functionalities

- **Frontend**:
  - Responsive web interface
  - Real-time device status updates
  - Interactive circuit designer
  - Bootstrap-based dark theme

## Cloud Backup Recommendations

To ensure data persistence and recovery capabilities, consider implementing the following backup strategies:

1. **Automated Local Backups**:
   - Regularly backup the TinyDB database file
   - Store fabric credentials securely
   - Export device configurations periodically

2. **Cloud Sync Options**:

   a. **Self-hosted Solution**:
   - Use Nextcloud or ownCloud for database backups
   - Implement automated sync using `rclone`
   - Keep encryption keys separate from backups

   b. **Managed Service Integration**:
   - AWS S3 or equivalent for database backups
   - Use AWS KMS or similar for key management
   - Implement versioning for rollback capability

3. **Backup Contents**:
   - Fabric credentials and certificates
   - Device pairing information
   - Virtual circuit configurations
   - Custom device names and groupings
   - Scene definitions

4. **Recovery Process**:
   - Document the restore procedure
   - Test recovery regularly
   - Maintain offline copies of critical credentials

### Implementation Suggestions

```python
# Example backup configuration
BACKUP_CONFIG = {
    'database': {
        'path': '/path/to/db',
        'frequency': '1h',
        'retention': '30d'
    },
    'credentials': {
        'path': '/path/to/creds',
        'frequency': '24h',
        'encryption': 'AES-256'
    },
    'fabric_info': {
        'path': '/path/to/fabric',
        'frequency': '1h'
    }
}
```

## Usage Examples

1. **Device Pairing**:
   ```
   1. Navigate to Devices > Pair New Device
   2. Enter the 8-digit setup code
   3. Follow the commissioning process
   ```

2. **Creating Virtual Circuits**:
   ```
   1. Go to Virtual Circuits
   2. Drag devices from the list to the canvas
   3. Select circuit type (switch/dimmer/color)
   4. Name your circuit
   5. Save the configuration
   ```

3. **Managing Fabrics**:
   ```
   1. View fabric information in device details
   2. Monitor fabric connections
   3. Handle multi-fabric device configurations
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- Report issues via GitHub Issues
- Join our community Discord for discussions
- Check the wiki for detailed documentation
