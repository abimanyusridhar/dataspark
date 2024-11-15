
from sqlalchemy import MetaData, inspect
from utils.db_connection import get_connection

def generate_schema():
    """Extract the database schema using SQLAlchemy."""
    engine = get_connection()
    if not engine:
        return None

    meta = MetaData()
    meta.reflect(bind=engine)
    return meta

def get_schema_details(schema):
    """Return detailed schema information including tables and relationships."""
    tables = {}
    relationships = {}
    
    if not schema:
        return tables, relationships

    engine = get_connection()
    inspector = inspect(engine)

    for table_name in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        pk = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
        fks = {
            fk['constrained_columns'][0]: fk['referred_table']
            for fk in inspector.get_foreign_keys(table_name) if fk.get('referred_table')
        }

        tables[table_name] = {
            'columns': columns,
            'primary_keys': pk,
            'foreign_keys': fks
        }

        # Track table relationships
        for fk_col, ref_table in fks.items():
            if ref_table not in relationships:
                relationships[ref_table] = []
            relationships[ref_table].append((table_name, fk_col))

    return tables, relationships

