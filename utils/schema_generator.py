from sqlalchemy import MetaData
from utils.db_connection import get_connection

def generate_schema():
    """Extracts the database schema using SQLAlchemy."""
    engine = get_connection()
    if not engine:
        return None
    
    meta = MetaData()
    meta.reflect(bind=engine)
    return meta

def get_schema_details(schema):
    """Returns a dictionary of tables and their columns."""
    tables = {}
    if not schema:
        return tables
    
    for table in schema.tables.values():
        columns = [col.name for col in table.columns]
        tables[table.name] = columns
    return tables
import os
from eralchemy import render_er
from utils.db_connection import get_connection

def generate_er_diagram():
    engine = get_connection()
    if engine:
        output_file = 'static/er_diagram.png'
        render_er(engine, output_file)
        return output_file
    return None