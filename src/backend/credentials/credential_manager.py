import os
from pathlib import Path
import json
import uuid
from ..logger import get_logger

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

    def _initialize_credentials(self, fabric_id=None, vendor_id=None):
        """Initialize empty credentials file with a new fabric ID."""
        try:
            default_creds = {
                'fabric_id': fabric_id or str(uuid.uuid4()),  # Use provided ID or generate new
                'vendor_id': vendor_id or '0xFFF1',  # Use provided ID or use default
                'operational_credentials': None,
                'devices': {}
            }
            self.save_credentials(default_creds)
            logger.info(f"Initialized new fabric with ID: {default_creds['fabric_id']}")
        except Exception as e:
            logger.error(f"Failed to initialize credentials: {e}")
            raise

    def initialize_new_credentials(self, fabric_id=None, vendor_id=None):
        """Initialize new Matter fabric credentials."""
        try:
            logger.info("Initializing new Matter fabric credentials")

            # Create credentials structure with provided or default values
            credentials = {
                'fabric_id': fabric_id or str(uuid.uuid4()),
                'vendor_id': vendor_id or '0xFFF1',
                'operational_credentials': {
                    'fabric_id': fabric_id or str(uuid.uuid4()),
                    'root_cert': 'development_certificate',  # Placeholder
                    'operational_cert': 'development_certificate'  # Placeholder
                },
                'devices': {}
            }

            self.save_credentials(credentials)
            logger.info("Successfully initialized new credentials")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize new credentials: {e}")
            return False

    def delete_credentials(self):
        """Delete current Matter fabric credentials."""
        try:
            logger.info("Deleting Matter fabric credentials")
            if self.cred_file.exists():
                self.cred_file.unlink()  # Delete the file
                # Reinitialize with empty credentials
                self._initialize_credentials()
                logger.info("Successfully deleted credentials and reinitialized empty state")
                return True
            logger.info("No credentials file found to delete")
            return True
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False

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
            if creds.get('operational_credentials'):
                creds['operational_credentials']['fabric_id'] = new_fabric_id
            self.save_credentials(creds)
            logger.info(f"Successfully updated fabric ID from {old_id} to {new_fabric_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update fabric ID: {e}")
            return False

    def get_fabric_info(self):
        """Get current fabric information including operational status."""
        try:
            creds = self.load_credentials()
            fabric_info = {
                'fabric_id': creds.get('fabric_id'),
                'vendor_id': creds.get('vendor_id'),
                'operational_credentials': bool(creds.get('operational_credentials')),
                'device_count': len(creds.get('devices', {}))
            }
            logger.debug(f"Retrieved fabric info: {fabric_info}")
            return fabric_info
        except Exception as e:
            logger.error(f"Failed to get fabric info: {e}")
            return None