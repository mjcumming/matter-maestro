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

        if not self.cred_file.exists():
            self._initialize_credentials()

    def _initialize_credentials(self):
        """Initialize empty credentials file with a new fabric ID."""
        default_creds = {
            'fabric_id': str(uuid.uuid4()),  # Generate a unique fabric ID
            'vendor_id': '0xFFF1',  # Default vendor ID for development
            'operational_credentials': None,
            'devices': {}
        }
        self.save_credentials(default_creds)
        logger.info(f"Initialized new fabric with ID: {default_creds['fabric_id']}")

    def save_credentials(self, credentials):
        """Save credentials to file."""
        try:
            with open(self.cred_file, 'w') as f:
                json.dump(credentials, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise

    def load_credentials(self):
        """Load credentials from file."""
        try:
            with open(self.cred_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise

    def update_fabric_id(self, new_fabric_id):
        """Update the fabric ID."""
        try:
            creds = self.load_credentials()
            creds['fabric_id'] = new_fabric_id
            self.save_credentials(creds)
            logger.info(f"Updated fabric ID to: {new_fabric_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update fabric ID: {e}")
            return False

    def store_operational_credentials(self, credentials):
        """Store operational credentials for the fabric."""
        try:
            creds = self.load_credentials()
            creds['operational_credentials'] = credentials
            self.save_credentials(creds)
            logger.info("Stored new operational credentials")
            return True
        except Exception as e:
            logger.error(f"Failed to store operational credentials: {e}")
            return False