import os
from flask import Flask, render_template, request, redirect, url_for, flash
from utils.db_connection import connect_to_db, get_connection
from utils.schema_generator import generate_schema, get_schema_details

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global variable to store selected database details
selected_db = None

# Ensure the uploaded_databases folder exists
UPLOAD_FOLDER = 'uploaded_databases'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/select_db', methods=['GET', 'POST'])
def select_db():
    """Page for selecting or uploading a database."""
    global selected_db
    if request.method == 'POST':
        db_type = request.form['db_type']
        
        # Handle SQLite database upload
        if db_type == 'sqlite':
            file = request.files['db_file']
            if file and file.filename.endswith('.db'):
                # Save the uploaded file to the 'uploaded_databases' folder
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                selected_db = {'type': 'sqlite', 'file_path': file_path}
                flash('SQLite database selected successfully!', 'success')
                return redirect(url_for('connect_database'))
            else:
                flash('Invalid file format. Please upload a .db file.', 'danger')
                return redirect(url_for('select_db'))
        
        # Handle MySQL/PostgreSQL database connection
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
            flash('MySQL database selected successfully!', 'success')
            return redirect(url_for('connect_database'))
    
    return render_template('select_db.html')

@app.route('/connect')
def connect_database():
    """Connect to the selected database and display schema."""
    global selected_db
    if selected_db:
        connection_status = connect_to_db(selected_db)
        if connection_status:
            # Get the schema and relationships
            tables, relationships = get_schema_details(generate_schema())
            
            # Pass the tables and relationships separately to the template
            return render_template('schema.html', tables=tables, relationships=relationships)
        else:
            flash('Failed to connect to the database', 'danger')
            return redirect(url_for('select_db'))
    flash('No database selected', 'warning')
    return redirect(url_for('select_db'))

if __name__ == "__main__":
    app.run(debug=True)
