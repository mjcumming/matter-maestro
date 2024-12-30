"""Scene Manager for handling Matter scene configurations and virtual devices."""
import json
from pathlib import Path
from ..logger import get_logger
import uuid

logger = get_logger(__name__)

class SceneManager:
    def __init__(self):
        self.scenes_dir = Path.home() / '.matter-maestro' / 'scenes'
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_file = self.scenes_dir / 'scenes.json'
        
        if not self.scenes_file.exists():
            self._initialize_scenes()
    
    def _initialize_scenes(self):
        """Initialize empty scenes file."""
        default_scenes = {
            'scenes': {},
            'virtual_devices': {}
        }
        self.save_scenes(default_scenes)
        logger.info("Initialized new scenes configuration")
    
    def save_scenes(self, scenes_data):
        """Save scenes to file."""
        try:
            with open(self.scenes_file, 'w') as f:
                json.dump(scenes_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save scenes: {e}")
            raise

    def load_scenes(self):
        """Load scenes from file."""
        try:
            with open(self.scenes_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load scenes: {e}")
            raise

    def create_scene(self, name, devices):
        """Create a new scene with specified device states."""
        try:
            scenes_data = self.load_scenes()
            scene_id = str(uuid.uuid4())
            
            scenes_data['scenes'][scene_id] = {
                'id': scene_id,
                'name': name,
                'devices': devices,
                'virtual_device_id': str(uuid.uuid4())  # Generate virtual device ID
            }
            
            # Create corresponding virtual device
            scenes_data['virtual_devices'][scene_id] = {
                'id': scenes_data['scenes'][scene_id]['virtual_device_id'],
                'type': 'switch',
                'name': f"Scene: {name}",
                'scene_id': scene_id
            }
            
            self.save_scenes(scenes_data)
            logger.info(f"Created new scene: {name} with ID: {scene_id}")
            return scene_id
        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return None

    def get_scene(self, scene_id):
        """Get scene by ID."""
        try:
            scenes_data = self.load_scenes()
            return scenes_data['scenes'].get(scene_id)
        except Exception as e:
            logger.error(f"Failed to get scene {scene_id}: {e}")
            return None

    def get_all_scenes(self):
        """Get all scenes."""
        try:
            scenes_data = self.load_scenes()
            return list(scenes_data['scenes'].values())
        except Exception as e:
            logger.error(f"Failed to get scenes: {e}")
            return []

    def update_scene(self, scene_id, name, devices):
        """Update an existing scene."""
        try:
            scenes_data = self.load_scenes()
            if scene_id not in scenes_data['scenes']:
                return False
            
            scenes_data['scenes'][scene_id].update({
                'name': name,
                'devices': devices
            })
            
            # Update virtual device name
            scenes_data['virtual_devices'][scene_id]['name'] = f"Scene: {name}"
            
            self.save_scenes(scenes_data)
            logger.info(f"Updated scene: {scene_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update scene {scene_id}: {e}")
            return False

    def delete_scene(self, scene_id):
        """Delete a scene and its virtual device."""
        try:
            scenes_data = self.load_scenes()
            if scene_id not in scenes_data['scenes']:
                return False
            
            # Remove both scene and its virtual device
            del scenes_data['scenes'][scene_id]
            del scenes_data['virtual_devices'][scene_id]
            
            self.save_scenes(scenes_data)
            logger.info(f"Deleted scene: {scene_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete scene {scene_id}: {e}")
            return False

    def get_virtual_device(self, device_id):
        """Get virtual device by ID."""
        try:
            scenes_data = self.load_scenes()
            for device in scenes_data['virtual_devices'].values():
                if device['id'] == device_id:
                    return device
            return None
        except Exception as e:
            logger.error(f"Failed to get virtual device {device_id}: {e}")
            return None
