import os
from pathlib import Path
import json
from ..logger import get_logger

logger = get_logger(__name__)

class CredentialManager:
    def __init__(self):
        self.cred_dir = Path.home() / '.matter-maestro' / 'credentials'
        self.cred_dir.mkdir(parents=True, exist_ok=True)
        self.cred_file = self.cred_dir / 'fabric_credentials.json'
        
        if not self.cred_file.exists():
            self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize empty credentials file."""
        default_creds = {
            'fabric_id': None,
            'devices': {}
        }
        self.save_credentials(default_creds)
    
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
