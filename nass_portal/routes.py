from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from . import mail
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/registration')
def registration():
    # Clear any existing session data
    session.clear()
    # Remove any deadline checks and directly render the registration page
    return render_template('registration.html')

@bp.route('/registration_page_1', methods=['GET', 'POST'])
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
            
            return redirect(url_for('main.registration_page_2'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_1.html')
    return render_template('registration_page_1.html')

@bp.route('/registration_page_2', methods=['GET', 'POST'])
def registration_page_2():
    if not session.get('personnel_number'):
        flash('Please start from the beginning', 'error')
        return redirect(url_for('main.registration_page_1'))
    
    if request.method == 'POST':
        # ... rest of the code ...
        return redirect(url_for('main.registration_page_3'))
    return render_template('registration_page_2.html')

@bp.route('/courses')
def courses():
    return render_template('courses.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        try:
            # Create email message
            msg = Message(
                subject=f"Contact Form: {subject}",
                sender=email,
                recipients=[os.environ.get('MAIL_DEFAULT_SENDER')],
                body=f"""
                From: {name} <{email}>
                
                Message:
                {message}
                """
            )
            
            # Send email
            mail.send(msg)
            
            flash('Thank you for your message. We will get back to you soon!', 'success')
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")  # For debugging
            flash('An error occurred while sending your message. Please try again.', 'error')
            return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        if admin and check_password_hash(admin['password'], password):
            session['logged_in'] = True
            session['user_id'] = admin['id']
            return redirect(url_for('main.admin_dashboard'))
        else:
            error = 'Invalid credentials'
    return render_template('admin_login.html', error=error)

@bp.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('main.admin_login'))
    return render_template('admin.html')

@bp.route('/students')
def student_list():
    if not session.get('logged_in'):
        return redirect(url_for('main.admin_login'))
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('student_list.html', students=students)

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('main.index'))








