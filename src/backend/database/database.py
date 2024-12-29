from tinydb import TinyDB
from pathlib import Path
import appdirs
import os

def initialize_db():
    """Initialize TinyDB database in user data directory."""
    data_dir = appdirs.user_data_dir("matter-maestro")
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = Path(data_dir) / "matter_maestro.json"
    return TinyDB(db_path)

def get_table(db, table_name):
    """Get or create a table in the database."""
    return db.table(table_name)
