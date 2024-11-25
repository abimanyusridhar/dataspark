from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from utils.db_connection import connect_to_db, get_connection
from utils.schema_generator import generate_schema, get_schema_details
from transformers import pipeline
from sqlalchemy.sql import text
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Folder for uploaded databases
UPLOAD_FOLDER = 'uploaded_databases'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# NLP Model for text-to-text SQL generation
nlp_model = pipeline('text2text-generation', model="t5-small")

# Store selected database globally
selected_db = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/select_db', methods=['GET', 'POST'])
def select_db():
    global selected_db
    if request.method == 'POST':
        db_type = request.form['db_type']
        if db_type == 'sqlite':
            file = request.files['db_file']
            if file and file.filename.endswith('.db'):
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                selected_db = {'type': 'sqlite', 'file_path': file_path}
                flash('SQLite database uploaded successfully!', 'success')
                return redirect(url_for('connect_database'))
        else:
            selected_db = {
                'type': 'mysql',
                'host': request.form['host'],
                'user': request.form['user'],
                'password': request.form['password'],
                'database': request.form['database']
            }
            flash('MySQL database connected successfully!', 'success')
            return redirect(url_for('connect_database'))
    return render_template('select_db.html')


@app.route('/connect')
def connect_database():
    global selected_db
    if selected_db:
        connection_status = connect_to_db(selected_db)
        if connection_status:
            schema = generate_schema()
            tables, relationships = get_schema_details(schema)
            return render_template('schema.html', tables=tables, relationships=relationships)
    flash('Failed to connect to the database', 'danger')
    return redirect(url_for('select_db'))


@app.route('/nlp_query', methods=['GET', 'POST'])
def nlp_query():
    if request.method == 'POST':
        natural_language_query = request.form.get('nl_query')
        if not natural_language_query:
            flash('Query cannot be empty.', 'danger')
            return redirect(url_for('nlp_query'))

        # Generate schema and SQL query
        schema = generate_schema()
        schema_metadata = get_schema_details(schema)[0]
        sql_query = generate_sql(natural_language_query, schema_metadata)

        if not sql_query:
            flash('Failed to generate SQL query from the provided input.', 'danger')
            return redirect(url_for('nlp_query'))

        # Execute the query
        connection = get_connection()
        try:
            with connection.connect() as conn:
                cursor = conn.execute(text(sql_query))
                columns = [col[0] for col in cursor.keys()] if cursor.returns_rows else []
                rows = cursor.fetchall() if columns else []
                if not rows:
                    flash('Query executed successfully, but no data was returned.', 'success')
                return render_template('result.html', columns=columns, rows=rows)
        except Exception as e:
            flash(f"Error executing the query: {e}", 'danger')
            return redirect(url_for('nlp_query'))

    return render_template('nlp_query.html')


def generate_sql(natural_language_query, schema_metadata):
    """Generate SQL from natural language query using NLP model."""
    try:
        schema_context = json.dumps(schema_metadata, indent=2)
        prompt = f"Schema:\n{schema_context}\n\nQuery: {natural_language_query}\n\nSQL:"
        result = nlp_model(prompt, max_length=200, num_return_sequences=1)
        return result[0]['generated_text'].strip()
    except Exception as e:
        print(f"Error in SQL generation: {e}")
        return None


def execute_query_with_sql(sql_query):
    """Execute a SQL query and return the results."""
    connection = get_connection()
    try:
        with connection.connect() as conn:
            cursor = conn.execute(text(sql_query))
            columns = [col[0] for col in cursor.keys()] if cursor.returns_rows else []
            rows = cursor.fetchall() if columns else []
            return columns, rows, None
    except Exception as e:
        return None, None, str(e)


if __name__ == "__main__":
    app.run(debug=True)
