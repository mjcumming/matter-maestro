import os
from pathlib import Path
import json
from ..logger import get_logger
import uuid

logger = get_logger(__name__)

class CredentialManager:
    def __init__(self):
        self.cred_dir = Path.home() / '.matter-maestro' / 'credentials'
        self.cred_dir.mkdir(parents=True, exist_ok=True)
        self.cred_file = self.cred_dir / 'fabric_credentials.json'
        logger.debug(f"Initializing CredentialManager with directory: {self.cred_dir}")

        if not self.cred_file.exists():
            logger.info("No existing credentials file found, initializing new one")
            self._initialize_credentials()
        else:
            logger.info("Found existing credentials file")

    def _initialize_credentials(self):
        """Initialize empty credentials file with a new fabric ID."""
        try:
            default_creds = {
                'fabric_id': str(uuid.uuid4()),  # Generate a unique fabric ID
                'vendor_id': '0xFFF1',  # Default vendor ID for development
                'operational_credentials': None,
                'devices': {}
            }
            self.save_credentials(default_creds)
            logger.info(f"Initialized new fabric with ID: {default_creds['fabric_id']}")
        except Exception as e:
            logger.error(f"Failed to initialize credentials: {e}")
            raise

    def save_credentials(self, credentials):
        """Save credentials to file."""
        try:
            logger.debug(f"Saving credentials to {self.cred_file}")
            with open(self.cred_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            logger.info("Credentials saved successfully")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise

    def load_credentials(self):
        """Load credentials from file."""
        try:
            logger.debug(f"Loading credentials from {self.cred_file}")
            if not self.cred_file.exists():
                logger.error("Credentials file not found")
                raise FileNotFoundError("Credentials file does not exist")

            with open(self.cred_file, 'r') as f:
                creds = json.load(f)
            logger.debug(f"Loaded credentials with fabric ID: {creds.get('fabric_id', 'Not Set')}")
            return creds
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse credentials file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise

    def update_fabric_id(self, new_fabric_id):
        """Update the fabric ID."""
        try:
            logger.info(f"Updating fabric ID to: {new_fabric_id}")
            creds = self.load_credentials()
            old_id = creds.get('fabric_id')
            creds['fabric_id'] = new_fabric_id
            self.save_credentials(creds)
            logger.info(f"Successfully updated fabric ID from {old_id} to {new_fabric_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update fabric ID: {e}")
            return False

    def store_operational_credentials(self, credentials):
        """Store operational credentials for the fabric."""
        try:
            logger.info("Storing new operational credentials")
            creds = self.load_credentials()
            creds['operational_credentials'] = credentials
            self.save_credentials(creds)
            logger.info("Successfully stored new operational credentials")
            return True
        except Exception as e:
            logger.error(f"Failed to store operational credentials: {e}")
            return False

    def get_fabric_info(self):
        """Get current fabric information including operational status."""
        try:
            creds = self.load_credentials()
            fabric_info = {
                'fabric_id': creds.get('fabric_id'),
                'vendor_id': creds.get('vendor_id'),
                'has_operational_credentials': bool(creds.get('operational_credentials')),
                'device_count': len(creds.get('devices', {}))
            }
            logger.debug(f"Retrieved fabric info: {fabric_info}")
            return fabric_info
        except Exception as e:
            logger.error(f"Failed to get fabric info: {e}")
            return None