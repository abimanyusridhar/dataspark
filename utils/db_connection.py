from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

engine = None

def connect_to_db(db_details):
    """Connect to the selected database."""
    global engine
    try:
        if db_details['type'] == 'sqlite':
            db_url = f"sqlite:///{db_details['file_path']}"
        else:
            db_url = f"mysql+pymysql://{db_details['user']}:{db_details['password']}@{db_details['host']}/{db_details['database']}"
        engine = create_engine(db_url)
        return engine.connect() is not None
    except SQLAlchemyError as e:
        print(f"Error connecting to database: {e}")
        return False

def get_connection():
    """Return the global engine connection."""
    return engine
