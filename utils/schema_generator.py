from sqlalchemy import MetaData, inspect
from utils.db_connection import get_connection

def generate_schema():
    """Extracts the database schema using SQLAlchemy."""
    engine = get_connection()
    if not engine:
        return None

    # Explicitly bind MetaData to the engine
    meta = MetaData()
    meta.reflect(bind=engine)
    return meta

def get_schema_details(schema):
    """Returns a dictionary with detailed schema information."""
    tables = {}
    relationships = {}
    if not schema:
        return tables, relationships

    # Get a connection from the engine
    engine = get_connection()
    if not engine:
        return tables, relationships

    inspector = inspect(engine)
    
    for table_name in inspector.get_table_names():
        # Get columns in the table
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # Handle primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_columns = pk_constraint.get('constrained_columns')
        if isinstance(pk_columns, list):
            pk = pk_columns
        else:
            pk = []

        # Handle foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        fks = {}
        for fk in foreign_keys:
            # Ensure the foreign key data is in the expected format
            if fk.get('constrained_columns') and fk.get('referred_table'):
                fks[fk['constrained_columns'][0]] = fk['referred_table']
        
        tables[table_name] = {
            'columns': columns,
            'primary_keys': pk,
            'foreign_keys': fks
        }

        # Extract relationships based on foreign keys
        for fk_col, ref_table in fks.items():
            if ref_table not in relationships:
                relationships[ref_table] = []
            relationships[ref_table].append((table_name, fk_col))

    return tables, relationships
