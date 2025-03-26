from flask import Flask, render_template, request, jsonify, send_file, flash
import qrcode
import os
import logging
from datetime import datetime
import pyodbc
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure logging
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('notepad.log', maxBytes=10000, backupCount=3)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# SQL Server configuration
DB_CONFIG = {
    'driver': 'SQL Server',
    'server': r'LENOVO\MSSQLSERVER01',
    'database': 'NotesDB',
    'username': 'mahesh1234',
    'password': '1234'
}

def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, make sure we're using the right database
        cursor.execute(f"USE NotesDB")
        
        # Create notes table with explicit schema
        cursor.execute('''
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'notes'
            )
            BEGIN
                CREATE TABLE dbo.notes (
                    note_id VARCHAR(50) PRIMARY KEY,
                    content TEXT,
                    title VARCHAR(255),
                    created_at DATETIME,
                    last_modified DATETIME,
                    tags VARCHAR(255),
                    is_archived BIT DEFAULT 0
                )
            END
        ''')
        
        # Create activity log table
        cursor.execute('''
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'activity_log'
            )
            BEGIN
                CREATE TABLE dbo.activity_log (
                    log_id INT IDENTITY(1,1) PRIMARY KEY,
                    action_type VARCHAR(50),
                    note_id VARCHAR(50),
                    action_timestamp DATETIME,
                    details TEXT
                )
            END
        ''')
        
        conn.commit()
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_note', methods=['POST'])
def create_note():
    try:
        data = request.json
        content = data.get('content', '')
        title = data.get('title', 'Untitled')
        tags = data.get('tags', '')
        
        note_id = str(datetime.now().timestamp())
        current_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert note
        cursor.execute('''
            INSERT INTO notes (note_id, content, title, created_at, last_modified, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (note_id, content, title, current_time, current_time, tags))
        
        # Log activity
        cursor.execute('''
            INSERT INTO activity_log (action_type, note_id, action_timestamp, details)
            VALUES (?, ?, ?, ?)
        ''', ('CREATE', note_id, current_time, f'Note created with title: {title}'))
        
        conn.commit()
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'http://localhost:5000/note/{note_id}')
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        os.makedirs('static/qr_codes', exist_ok=True)
        qr_path = f'static/qr_codes/{note_id}.png'
        qr_img.save(qr_path)
        
        logger.info(f"Note created successfully: {note_id}")
        return jsonify({
            'success': True,
            'note_id': note_id,
            'qr_code_url': f'/static/qr_codes/{note_id}.png',
            'message': 'Note created successfully!'
        })
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/note/<note_id>')
def view_note(note_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if note exists
        cursor.execute('SELECT * FROM notes WHERE note_id = ?', (note_id,))
        note = cursor.fetchone()
        
        if note:
            return render_template('note.html', note_id=note_id)
        return "Note not found", 404
    except Exception as e:
        logger.error(f"Error viewing note: {str(e)}")
        return "Error loading note", 500
    finally:
        conn.close()

@app.route('/api/note/<note_id>', methods=['GET'])
def get_note(note_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM notes WHERE note_id = ?', (note_id,))
        note = cursor.fetchone()
        
        if note:
            return jsonify({
                'content': note[1],  # content
                'title': note[2],    # title
                'created_at': note[3].isoformat() if note[3] else None,
                'last_modified': note[4].isoformat() if note[4] else None,
                'tags': note[5]      # tags
            })
        return "Note not found", 404
    except Exception as e:
        logger.error(f"Error retrieving note: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/note/<note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        content = request.json.get('content', '')
        title = request.json.get('title', '')
        tags = request.json.get('tags', '')
        current_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if note exists
        cursor.execute('SELECT * FROM notes WHERE note_id = ?', (note_id,))
        note = cursor.fetchone()
        
        if note:
            # Update note
            cursor.execute('''
                UPDATE notes 
                SET content = ?, title = ?, tags = ?, last_modified = ?
                WHERE note_id = ?
            ''', (content, title, tags, current_time, note_id))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_log (action_type, note_id, action_timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', ('UPDATE', note_id, current_time, 'Note updated'))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Note updated successfully',
                'last_modified': current_time.isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        conn.close()

# Make sure to call init_db() when the application starts
if __name__ == '__main__':
    try:
        init_db()  # Initialize database tables before running the app
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to initialize application: {str(e)}") 