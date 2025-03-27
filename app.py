from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash # Import security functions

app = Flask(__name__)
app.secret_key = "secret_key"  # Change this to a strong, random key
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')  # Corrected database path

def get_db():
    """
    Establishes and returns a database connection. Uses application context.
    """
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Database connection error: {e}") # Log the error
            # Consider raising the exception or handling it appropriately for your application
            raise  # Re-raise to prevent further execution with a broken DB connection
    return g.db

def close_db(e=None):
    """
    Closes the database connection if it exists. Used as a teardown.
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except sqlite3.Error as e:
            print(f"Database closing error: {e}") #log error.

def init_db():
    """Initializes the database schema."""
    with app.app_context():  # push app context
        db = get_db()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                db.executescript(f.read())
            db.commit()
        except sqlite3.Error as e:
            print(f"Database error during init_db: {e}")
            db.rollback()
            raise  # Re-raise the error so the app doesn't run with a broken DB.

@app.cli.command('initdb')  # flask --app app.py initdb
def initdb_command():
    """Creates the database tables."""
    try:
        init_db()
        print('Initialized the database.')
    except Exception as e:
        print(f"Failed to initialize database: {e}")

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

@app.route('/registration')
def registration():
    return redirect(url_for('registration_page_1'))

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST']) # Changed route to /admin
def admin_login():
    error = None # Initialize error variable
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone() #prevent SQL injection
        if admin and check_password_hash(admin['password'], password): # Use the secure password check
            session['logged_in'] = True
            session['user_id'] = admin['id']  # Store user ID in session for later use
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials' # Set error message
    return render_template('admin_login.html', error=error) # Pass the error to the template

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
    session.pop('user_id', None) # Clear the user ID
    return redirect(url_for('index'))

@app.route('/registration_page_1', methods=['GET', 'POST'])
def registration_page_1():
    if request.method == 'POST':
        # Save data to session
        session['personnel_number'] = request.form['personnel_number']
        session['rank'] = request.form['rank']
        session['name'] = request.form['name']
        session['unit'] = request.form['unit']
        session['dob'] = request.form['dob']
        session['year_in_rank'] = request.form['year_in_rank']
        session['year_of_last_promotion'] = request.form['year_of_last_promotion']
        return redirect(url_for('registration_page_2'))
    return render_template('registration_page_1.html')

@app.route('/registration_page_2', methods=['GET', 'POST'])
def registration_page_2():
    if request.method == 'POST':
        # Save data to session
        session['nationality'] = request.form.get('nationality', '')
        session['marital_status'] = request.form.get('marital_status', '')
        session['state_of_origin'] = request.form.get('state_of_origin', '')
        session['permanent_address'] = request.form.get('permanent_address', '')
        return redirect(url_for('registration_page_3'))
    return render_template('registration_page_2.html')

@app.route('/registration_page_3', methods=['GET', 'POST'])
def registration_page_3():
    if request.method == 'POST':
        # Save data to session
        session['facebook'] = request.form['facebook']
        session['twitter'] = request.form['twitter']
        session['whatsapp'] = request.form['whatsapp']
        session['instagram'] = request.form['instagram']
        return redirect(url_for('registration_page_4'))
    return render_template('registration_page_3.html')

@app.route('/registration_page_4', methods=['GET', 'POST'])
def registration_page_4():
    if request.method == 'POST':
        # Save data to session
        session['nok_name_1'] = request.form['nok_name_1']
        session['nok_address_1'] = request.form['nok_address_1']
        session['nok_gsm_number_1'] = request.form['nok_gsm_number_1']
        session['nok_email_1'] = request.form['nok_email_1']
        return redirect(url_for('registration_page_5'))
    return render_template('registration_page_4.html')

@app.route('/registration_page_5', methods=['GET', 'POST'])
def registration_page_5():
    if request.method == 'POST':
        # Save data to session
        session['uni_serial'] = request.form.getlist('uni_serial[]')
        session['uni_name'] = request.form.getlist('uni_name[]')
        session['uni_year_from'] = request.form.getlist('uni_year_from[]')
        session['uni_year_to'] = request.form.getlist('uni_year_to[]')
        session['uni_cert'] = request.form.getlist('uni_cert[]')
        session['uni_grade'] = request.form.getlist('uni_grade[]')
        session['uni_remarks'] = request.form.getlist('uni_remarks[]')
        return redirect(url_for('registration_page_6'))
    return render_template('registration_page_5.html')

@app.route('/registration_page_6', methods=['GET', 'POST'])
def registration_page_6():
    if request.method == 'POST':
        # Save data to session
        session['military_serial'] = request.form.getlist('military_serial[]')
        session['military_name'] = request.form.getlist('military_name[]')
        session['military_year_from'] = request.form.getlist('military_year_from[]')
        session['military_year_to'] = request.form.getlist('military_year_to[]')
        session['military_cert'] = request.form.getlist('military_cert[]')
        session['military_grade'] = request.form.getlist('military_grade[]')
        session['military_remarks'] = request.form.getlist('military_remarks[]')
        return redirect(url_for('registration_page_7'))
    return render_template('registration_page_6.html')

@app.route('/registration_page_7', methods=['GET', 'POST'])
def registration_page_7():
    if request.method == 'POST':
        # Final submission logic
        # Here you would typically save the data to the database
        db = get_db()
        try:
            db.execute('''
                INSERT INTO students (
                    personnel_number, rank, name, unit, dob, year_in_rank, year_of_last_promotion,
                    nationality, marital_status, state_of_origin, permanent_address, facebook, twitter,
                    whatsapp, instagram, nok_name_1, nok_address_1, nok_gsm_number_1, nok_email_1,
                    uni_serial, uni_name, uni_year_from, uni_year_to, uni_cert, uni_grade, uni_remarks,
                    military_serial, military_name, military_year_from, military_year_to, military_cert,
                    military_grade, military_remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.get('personnel_number'), session.get('rank'), session.get('name'),
                session.get('unit'), session.get('dob'), session.get('year_in_rank'),
                session.get('year_of_last_promotion'), session.get('nationality'),
                session.get('marital_status'), session.get('state_of_origin'),
                session.get('permanent_address'), session.get('facebook'),
                session.get('twitter'), session.get('whatsapp'), session.get('instagram'),
                session.get('nok_name_1'), session.get('nok_address_1'),
                session.get('nok_gsm_number_1'), session.get('nok_email_1'),
                ','.join(session.get('uni_serial', [])), ','.join(session.get('uni_name', [])),
                ','.join(session.get('uni_year_from', [])), ','.join(session.get('uni_year_to', [])),
                ','.join(session.get('uni_cert', [])), ','.join(session.get('uni_grade', [])),
                ','.join(session.get('uni_remarks', [])),
                ','.join(session.get('military_serial', [])), ','.join(session.get('military_name', [])),
                ','.join(session.get('military_year_from', [])), ','.join(session.get('military_year_to', [])),
                ','.join(session.get('military_cert', [])), ','.join(session.get('military_grade', [])),
                ','.join(session.get('military_remarks', [])),
            ))
            db.commit()
            session.clear() # Clear the session data after successful submission
            return redirect(url_for('success'))  # Redirect to a success page
        except sqlite3.Error as e:
            db.rollback()
            print(f"Database error during registration: {e}")
            return render_template('registration_page_7.html', error="Failed to complete registration. Please try again.") # inform user
        finally:
            close_db()
    return render_template('registration_page_7.html')

@app.route('/success')
def success():
    return "Registration completed successfully!"
