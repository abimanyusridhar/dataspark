from flask import Flask, render_template, request, redirect, url_for, flash
from utils.db_connection import connect_to_db, get_connection
from utils.schema_generator import generate_schema, get_schema_details
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
selected_db = None

UPLOAD_FOLDER = 'uploaded_databases'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
            host = request.form['host']
            user = request.form['user']
            password = request.form['password']
            database = request.form['database']
            selected_db = {
                'type': 'mysql',
                'host': host,
                'user': user,
                'password': password,
                'database': database
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
            tables, relationships = get_schema_details(generate_schema())
            return render_template('schema.html', tables=tables, relationships=relationships)
    flash('Failed to connect to the database', 'danger')
    return redirect(url_for('select_db'))
from sqlalchemy import create_engine

def get_connection():
    if selected_db['type'] == 'sqlite':
        return create_engine(f"sqlite:///{selected_db['file_path']}")
    elif selected_db['type'] == 'mysql':
        return create_engine(
            f"mysql+pymysql://{selected_db['user']}:{selected_db['password']}@{selected_db['host']}/{selected_db['database']}"
        )


from sqlalchemy import text

@app.route('/execute_query', methods=['POST'])
def execute_query():
    query = request.form['sql_query']
    connection = get_connection()
    query_result = None

    if connection:
        try:
            # Use a connection context to execute the query
            with connection.connect() as conn:
                cursor = conn.execute(text(query))
                
                # Get the column names if there are results
                columns = [col[0] for col in cursor.keys()] if cursor.returns_rows else []
                rows = cursor.fetchall() if columns else []

                # Convert results to an HTML table
                if columns and rows:
                    result_html = "<h4>Query Results:</h4><table><thead><tr>"
                    result_html += "".join(f"<th>{col}</th>" for col in columns)
                    result_html += "</tr></thead><tbody>"
                    for row in rows:
                        result_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
                    result_html += "</tbody></table>"
                else:
                    result_html = "<p>No results found.</p>"

        except Exception as e:
            result_html = f"<p style='color: red;'>Error: {e}</p>"

        return result_html
    else:
        return "<p style='color: red;'>No database connection.</p>"

if __name__ == "__main__":
    app.run(debug=True)
