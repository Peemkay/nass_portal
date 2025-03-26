from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"  # Change this to a strong, random key
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db') # Corrected database path

def get_db():
    """
    Establishes and returns a database connection.  Uses application context.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Closes the database connection if it exists.  Used as a teardown.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    with app.app_context(): #push app context
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

@app.cli.command('initdb')  #flask --app app.py initdb
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')
    
@app.before_request
def before_request():
    """Ensures the database is connected before each request."""
    get_db()

@app.teardown_appcontext
def teardown_appcontext(e=None):
    """Closes the database connection after each request."""
    close_db()

# Define your routes here
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        email = request.form['email']
        db = get_db()
        try:
            db.execute('INSERT INTO students (name, course, email) VALUES (?, ?, ?)', (name, course, email))
            db.commit()
            return redirect(url_for('index'))  # Redirect on success
        except sqlite3.Error as e:
            error_message = f"Database error: {e}"
            return render_template('registration.html', error=error_message)
    return render_template('registration.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password)).fetchone()
        if admin:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/students')
def student_list():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('student_list.html', students=students)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))
