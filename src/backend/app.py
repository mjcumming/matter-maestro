from flask import Flask, render_template
from flasgger import Swagger
from .devices.routes import devices_blueprint
from .scenes.routes import scenes_blueprint
from .groups.routes import groups_blueprint
from .virtual_circuits.routes import virtual_circuits_blueprint
from .credentials.routes import credentials_blueprint
from .backup.routes import backup_blueprint
from .network.routes import network_blueprint
from .logger import get_logger
from .database.database import initialize_db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = get_logger(__name__)

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Matter Maestro API',
    'uiversion': 3,
    'specs_route': '/api/docs'
}
swagger = Swagger(app)

# Initialize database
db = initialize_db()

# Register UI routes with proper prefixes
app.register_blueprint(devices_blueprint, url_prefix="/devices", name="devices_ui")
app.register_blueprint(scenes_blueprint, url_prefix="/scenes", name="scenes_ui")
app.register_blueprint(groups_blueprint, url_prefix="/groups", name="groups_ui")
app.register_blueprint(virtual_circuits_blueprint, url_prefix="/virtual-circuits", name="virtual_circuits_ui")
app.register_blueprint(credentials_blueprint, url_prefix="/credentials", name="credentials_ui")
app.register_blueprint(backup_blueprint, url_prefix="/backup", name="backup_ui")

# Register API routes
app.register_blueprint(devices_blueprint, url_prefix="/api/devices", name="devices_api")
app.register_blueprint(scenes_blueprint, url_prefix="/api/scenes", name="scenes_api")
app.register_blueprint(groups_blueprint, url_prefix="/api/groups", name="groups_api")
app.register_blueprint(virtual_circuits_blueprint, url_prefix="/api/virtual-circuits", name="virtual_circuits_api")
app.register_blueprint(credentials_blueprint, url_prefix="/api/credentials", name="credentials_api")
app.register_blueprint(backup_blueprint, url_prefix="/api/backup", name="backup_api")
app.register_blueprint(network_blueprint, url_prefix="/api/network")

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return {'error': 'Internal server error'}, 500

if __name__ == "__main__":
    logger.info("Starting Matter Maestro application")
    app.run(host='0.0.0.0', port=5000, debug=True)