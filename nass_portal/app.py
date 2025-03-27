from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"  # Change this to a strong, random key
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')  # Corrected database path

def get_db():
    """
    Establishes and returns a database connection. Uses application context.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Closes the database connection if it exists. Used as a teardown.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    with app.app_context():  # push app context
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

@app.cli.command('initdb')  # flask --app app.py initdb
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

@app.route('/registration')
def registration():
    # Clear any existing session data when starting new registration
    session.clear()
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

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/registration_page_1', methods=['GET', 'POST'])
def registration_page_1():
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['personnel_number', 'rank', 'name', 'unit', 'dob', 
                             'year_in_rank', 'year_of_last_promotion']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_1.html')
            
            # Save data to session
            for field in required_fields:
                session[field] = request.form[field]
            
            return redirect(url_for('registration_page_2'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_1.html')
    return render_template('registration_page_1.html')

@app.route('/registration_page_2', methods=['GET', 'POST'])
def registration_page_2():
    if not session.get('personnel_number'):
        flash('Please start from the beginning', 'error')
        return redirect(url_for('registration_page_1'))
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['nationality', 'marital_status', 'state_of_origin', 
                             'permanent_address']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_2.html')
            
            # Save data to session
            session['nationality'] = request.form['nationality']
            session['marital_status'] = request.form['marital_status']
            session['state_of_origin'] = request.form['state_of_origin']
            session['permanent_address'] = request.form['permanent_address']
            
            return redirect(url_for('registration_page_3'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_2.html')
    return render_template('registration_page_2.html')

@app.route('/registration_page_3', methods=['GET', 'POST'])
def registration_page_3():
    if not session.get('nationality'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration_page_2'))
    
    if request.method == 'POST':
        try:
            # Save social media data (optional fields)
            session['facebook'] = request.form.get('facebook', '')
            session['twitter'] = request.form.get('twitter', '')
            session['whatsapp'] = request.form.get('whatsapp', '')
            session['instagram'] = request.form.get('instagram', '')
            
            return redirect(url_for('registration_page_4'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_3.html')
    return render_template('registration_page_3.html')

@app.route('/registration_page_4', methods=['GET', 'POST'])
def registration_page_4():
    if not session.get('whatsapp'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration_page_3'))
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['nok_name_1', 'nok_address_1', 'nok_gsm_number_1']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_4.html')
            
            # Save next of kin data
            session['nok_name_1'] = request.form['nok_name_1']
            session['nok_address_1'] = request.form['nok_address_1']
            session['nok_gsm_number_1'] = request.form['nok_gsm_number_1']
            session['nok_email_1'] = request.form.get('nok_email_1', '')
            
            return redirect(url_for('registration_page_5'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_4.html')
    return render_template('registration_page_4.html')

@app.route('/registration_page_5', methods=['GET', 'POST'])
def registration_page_5():
    if not session.get('nok_name_1'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration_page_4'))
    
    if request.method == 'POST':
        try:
            # Save academic records (array fields)
            session['uni_serial'] = request.form.getlist('uni_serial[]')
            session['uni_name'] = request.form.getlist('uni_name[]')
            session['uni_year_from'] = request.form.getlist('uni_year_from[]')
            session['uni_year_to'] = request.form.getlist('uni_year_to[]')
            session['uni_cert'] = request.form.getlist('uni_cert[]')
            session['uni_grade'] = request.form.getlist('uni_grade[]')
            session['uni_remarks'] = request.form.getlist('uni_remarks[]')
            
            return redirect(url_for('registration_page_6'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_5.html')
    return render_template('registration_page_5.html')

@app.route('/registration_page_6', methods=['GET', 'POST'])
def registration_page_6():
    if not session.get('uni_serial'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration_page_5'))
    
    if request.method == 'POST':
        try:
            # Save military course records (array fields)
            session['military_serial'] = request.form.getlist('military_serial[]')
            session['military_name'] = request.form.getlist('military_name[]')
            session['military_year_from'] = request.form.getlist('military_year_from[]')
            session['military_year_to'] = request.form.getlist('military_year_to[]')
            session['military_cert'] = request.form.getlist('military_cert[]')
            session['military_grade'] = request.form.getlist('military_grade[]')
            session['military_remarks'] = request.form.getlist('military_remarks[]')
            
            return redirect(url_for('registration_page_7'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_6.html')
    return render_template('registration_page_6.html')

@app.route('/registration_page_7', methods=['GET', 'POST'])
def registration_page_7():
    if not session.get('military_serial'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration_page_6'))
    
    if request.method == 'POST':
        db = get_db()
        try:
            # Insert all collected data into database
            db.execute('''
                INSERT INTO students (
                    personnel_number, rank, name, unit, dob, year_in_rank, 
                    year_of_last_promotion, nationality, marital_status, 
                    state_of_origin, permanent_address, facebook, twitter,
                    whatsapp, instagram, nok_name_1, nok_address_1, 
                    nok_gsm_number_1, nok_email_1, uni_serial, uni_name, 
                    uni_year_from, uni_year_to, uni_cert, uni_grade, 
                    uni_remarks, military_serial, military_name, 
                    military_year_from, military_year_to, military_cert,
                    military_grade, military_remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.get('personnel_number'), session.get('rank'),
                session.get('name'), session.get('unit'), session.get('dob'),
                session.get('year_in_rank'), session.get('year_of_last_promotion'),
                session.get('nationality'), session.get('marital_status'),
                session.get('state_of_origin'), session.get('permanent_address'),
                session.get('facebook'), session.get('twitter'),
                session.get('whatsapp'), session.get('instagram'),
                session.get('nok_name_1'), session.get('nok_address_1'),
                session.get('nok_gsm_number_1'), session.get('nok_email_1'),
                ','.join(session.get('uni_serial', [])),
                ','.join(session.get('uni_name', [])),
                ','.join(session.get('uni_year_from', [])),
                ','.join(session.get('uni_year_to', [])),
                ','.join(session.get('uni_cert', [])),
                ','.join(session.get('uni_grade', [])),
                ','.join(session.get('uni_remarks', [])),
                ','.join(session.get('military_serial', [])),
                ','.join(session.get('military_name', [])),
                ','.join(session.get('military_year_from', [])),
                ','.join(session.get('military_year_to', [])),
                ','.join(session.get('military_cert', [])),
                ','.join(session.get('military_grade', [])),
                ','.join(session.get('military_remarks', []))
            ))
            db.commit()
            session.clear()  # Clear session after successful submission
            return redirect(url_for('success'))
        except sqlite3.Error as e:
            db.rollback()
            flash('Database error occurred. Please try again.', 'error')
            return render_template('registration_page_7.html')
        finally:
            close_db()
    return render_template('registration_page_7.html')

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
