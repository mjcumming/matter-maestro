from flask import Flask, render_template
from flasgger import Swagger
from .devices.routes import devices_blueprint
from .scenes.routes import scenes_blueprint
from .groups.routes import groups_blueprint
from .virtual_circuits.routes import virtual_circuits_blueprint
from .credentials.routes import credentials_blueprint
from .backup.routes import backup_blueprint  # Add backup blueprint import
from .logger import get_logger
from .database.database import initialize_db

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

# Register blueprints
app.register_blueprint(devices_blueprint, url_prefix="/api/devices")
app.register_blueprint(scenes_blueprint, url_prefix="/api/scenes")
app.register_blueprint(groups_blueprint, url_prefix="/api/groups")
app.register_blueprint(virtual_circuits_blueprint, url_prefix="/api/virtual-circuits")
app.register_blueprint(credentials_blueprint, url_prefix="/api/credentials")
app.register_blueprint(backup_blueprint, url_prefix="/api/backup")  # Register backup blueprint

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
    app.run(host='0.0.0.0', port=5000, debug=True)