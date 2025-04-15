from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_mail import Message
from . import mail
import os
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from .db import get_db
from .registration_utils import is_registration_open, get_registration_status

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename, extensions=None):
    if extensions is None:
        extensions = ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/registration')
def registration():
    # Clear any existing session data
    session.clear()

    # Get registration status
    reg_status = get_registration_status()

    return render_template('registration.html', reg_status=reg_status)

@bp.route('/registration_page_1', methods=['GET', 'POST'])
def registration_page_1():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if request.method == 'POST':
        try:
            # Store form data temporarily
            form_data = {
                'service_number': request.form.get('service_number'),
                'rank': request.form.get('rank'),
                'surname': request.form.get('surname'),
                'other_names': request.form.get('other_names'),
                'date_of_birth': request.form.get('date_of_birth'),
                'gender': request.form.get('gender'),
                'current_unit': request.form.get('current_unit'),
                'date_of_commission': request.form.get('date_of_commission'),
                'years_in_service': request.form.get('years_in_service'),
                'nationality': request.form.get('nationality', 'Nigerian')
            }

            # Validate required fields
            required_fields = {
                'service_number': 'Service Number',
                'rank': 'Rank',
                'surname': 'Surname',
                'other_names': 'Other Names',
                'date_of_birth': 'Date of Birth',
                'gender': 'Gender',
                'current_unit': 'Current Unit',
                'date_of_commission': 'Date of Commission/Enlistment',
                'years_in_service': 'Years in Service',
                'nationality': 'Nationality'
            }

            # Check for missing fields
            missing_fields = []
            for field, display_name in required_fields.items():
                if not form_data.get(field):
                    missing_fields.append(display_name)

            if missing_fields:
                flash(f"Required fields missing: {', '.join(missing_fields)}", 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            # Handle passport photo upload
            if 'passport_photo' not in request.files:
                flash('Passport photograph is required', 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            photo = request.files['passport_photo']
            if photo.filename == '':
                flash('No selected file for passport photograph', 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            # Enhanced validation logic
            try:
                # Validate date fields
                dob = datetime.strptime(form_data['date_of_birth'], '%Y-%m-%d')
                commission_date = datetime.strptime(form_data['date_of_commission'], '%Y-%m-%d')

                # Date validations
                if dob > datetime.now():
                    flash('Date of birth cannot be in the future', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                if commission_date > datetime.now():
                    flash('Date of commission cannot be in the future', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # Rank validation
                valid_ranks = [
                    # Non-Commissioned Ranks
                    'recruit', 'private', 'lance corporal', 'corporal', 'sergeant',
                    'staff sergeant', 'warrant officer', 'master warrant officer',
                    'army warrant officer',
                    # Commissioned Ranks
                    'second lieutenant', 'lieutenant', 'captain', 'major',
                    'lieutenant colonel', 'colonel', 'brigadier general',
                    'major general', 'lieutenant general', 'general'
                ]
                if form_data['rank'].lower() not in valid_ranks:
                    flash('Invalid rank selected', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # Calculate years in service based on date of commission
                today = datetime.now()
                years_in_service = today.year - commission_date.year
                if today.month < commission_date.month or (today.month == commission_date.month and today.day < commission_date.day):
                    years_in_service -= 1

                # Validate the calculated years in service
                if years_in_service < 0 or years_in_service > 40:
                    flash('Years in service must be between 0 and 40', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # Update the form_data with the calculated value
                form_data['years_in_service'] = str(years_in_service)

                # Name validations
                if len(form_data['surname']) < 2 or len(form_data['other_names']) < 2:
                    flash('Names must be at least 2 characters long', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                if not all(c.isalpha() or c.isspace() for c in form_data['surname'] + form_data['other_names']):
                    flash('Names should contain only letters and spaces', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # Current unit validation
                if len(form_data['current_unit']) < 2:
                    flash('Current unit must be at least 2 characters long', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # Gender validation
                if form_data['gender'].lower() not in ['male', 'female']:
                    flash('Invalid gender selection', 'error')
                    return render_template('registration_page_1.html', form_data=form_data)

                # If all validations pass, store in session
                for field in form_data:
                    session[field] = form_data[field]

            except Exception as e:
                current_app.logger.error(f"Validation error: {str(e)}")
                flash('An error occurred during validation. Please try again.', 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            # Save form data to session
            for field in form_data:
                session[field] = form_data[field]

            session['page_1_complete'] = True

            # Handle file upload
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                # Create unique filename using service number and timestamp
                file_ext = filename.rsplit('.', 1)[1].lower()
                # Sanitize service number to remove any slashes or special characters
                safe_service_number = secure_filename(form_data['service_number'])
                unique_filename = f"{safe_service_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"

                # Ensure upload directory exists
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'passport_photos')
                os.makedirs(upload_dir, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_dir, unique_filename)
                photo.save(file_path)

                # Store the file path in session
                session['passport_photo'] = unique_filename
            else:
                flash('Invalid file type. Please upload a valid image file (PNG, JPG, JPEG)', 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            # Get database connection
            from .db import get_db
            db = get_db()

            try:
                # Check if service number already exists
                existing = db.execute(
                    'SELECT id FROM students WHERE service_number = ?',
                    (form_data['service_number'],)
                ).fetchone()

                if existing:
                    # Update existing record
                    db.execute('''
                        UPDATE students SET
                            rank = ?, surname = ?, other_names = ?,
                            date_of_birth = ?, gender = ?, current_unit = ?,
                            date_of_commission = ?, years_in_service = ?,
                            passport_photo = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE service_number = ?
                    ''', (
                        form_data['rank'], form_data['surname'],
                        form_data['other_names'], form_data['date_of_birth'],
                        form_data['gender'], form_data['current_unit'],
                        form_data['date_of_commission'], form_data['years_in_service'],
                        session['passport_photo'], form_data['service_number']
                    ))
                else:
                    # Insert new record
                    db.execute('''
                        INSERT INTO students (
                            service_number, rank, surname, other_names,
                            date_of_birth, gender, current_unit,
                            date_of_commission, years_in_service,
                            passport_photo, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        form_data['service_number'], form_data['rank'],
                        form_data['surname'], form_data['other_names'],
                        form_data['date_of_birth'], form_data['gender'],
                        form_data['current_unit'], form_data['date_of_commission'],
                        form_data['years_in_service'], session['passport_photo']
                    ))

                db.commit()

            except Exception as e:
                db.rollback()
                current_app.logger.error(f"Database error: {str(e)}")
                flash('Error saving data. Please try again.', 'error')
                return render_template('registration_page_1.html', form_data=form_data)

            # If everything is valid, proceed to next page
            return redirect(url_for('main.registration_page_2'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 1: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            # Return the form with the data that was submitted
            return render_template('registration_page_1.html', form_data=request.form)

    # GET request - show the form
    # Use session data if available, otherwise empty dict
    form_data = {}
    for field in ['service_number', 'rank', 'surname', 'other_names',
                  'date_of_birth', 'gender', 'current_unit',
                  'date_of_commission', 'years_in_service', 'nationality']:
        if field in session:
            form_data[field] = session[field]

    return render_template('registration_page_1.html', form_data=form_data)

@bp.route('/registration_page_2', methods=['GET', 'POST'])
def registration_page_2():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_1_complete'):
        flash('Please complete page 1 first', 'error')
        return redirect(url_for('main.registration_page_1'))

    if request.method == 'POST':
        try:
            required_fields = [
                'marital_status', 'state_of_origin',
                'permanent_address', 'phone_number', 'email'
            ]

            # Hard fix for nationality - ensure it's already in the session from page 1
            if 'nationality' not in session or not session['nationality']:
                # If nationality is missing, check if it's in the current form
                if request.form.get('nationality'):
                    session['nationality'] = request.form.get('nationality')
                else:
                    # Set a default value as a fallback
                    session['nationality'] = 'Nigerian'

            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_2.html', form_data=request.form)

            for field in required_fields:
                session[field] = request.form[field]
            session['page_2_complete'] = True

            return redirect(url_for('main.registration_page_3'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 2: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_2.html', form_data=request.form)

    return render_template('registration_page_2.html', form_data={})

@bp.route('/registration_page_3', methods=['GET', 'POST'])
def registration_page_3():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_2_complete'):
        flash('Please complete page 2 first', 'error')
        return redirect(url_for('main.registration_page_2'))

    if request.method == 'POST':
        try:
            social_fields = ['facebook', 'twitter', 'whatsapp', 'instagram']

            if not request.form.get('whatsapp'):
                flash('WhatsApp number is required', 'error')
                return render_template('registration_page_3.html', form_data=request.form)

            whatsapp = request.form.get('whatsapp')
            if not whatsapp.replace('+', '').replace(' ', '').isdigit():
                flash('Please enter a valid WhatsApp number', 'error')
                return render_template('registration_page_3.html', form_data=request.form)

            for field in social_fields:
                session[field] = request.form.get(field, '').strip()
            session['page_3_complete'] = True

            return redirect(url_for('main.registration_page_4'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 3: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_3.html', form_data=request.form)

    return render_template('registration_page_3.html', form_data={})

@bp.route('/registration_page_4', methods=['GET', 'POST'])
def registration_page_4():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_3_complete'):
        flash('Please complete page 3 first', 'error')
        return redirect(url_for('main.registration_page_3'))

    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['nok_name_1', 'nok_relationship_1', 'nok_address_1', 'nok_gsm_number_1']

            # Hard fix for nok_phone_1 issue - check both possible field names
            if not request.form.get('nok_gsm_number_1') and not request.form.get('nok_phone_1'):
                # If neither field is present, use a default value or show an error
                if 'nok_phone_1' in request.form:
                    request.form = request.form.copy()  # Make mutable
                    request.form['nok_gsm_number_1'] = request.form['nok_phone_1']
                else:
                    flash('Next of Kin Phone Number is required', 'error')
                    return render_template('registration_page_4.html', form_data=request.form)

            # Continue with other validations
            for field in required_fields:
                if field != 'nok_gsm_number_1' and not request.form.get(field):  # Skip phone check as we handled it above
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_4.html', form_data=request.form)

            # Save next of kin data
            nok_fields = ['nok_name_1', 'nok_relationship_1', 'nok_address_1', 'nok_gsm_number_1', 'nok_email_1',
                         'nok_name_2', 'nok_relationship_2', 'nok_address_2', 'nok_gsm_number_2', 'nok_email_2']

            for field in nok_fields:
                # Special handling for phone field
                if field == 'nok_gsm_number_1' and not request.form.get(field) and request.form.get('nok_phone_1'):
                    session[field] = request.form.get('nok_phone_1', '').strip()
                    # Also store in the alternate field name for compatibility
                    session['nok_phone_1'] = request.form.get('nok_phone_1', '').strip()
                else:
                    session[field] = request.form.get(field, '').strip()

            session['page_4_complete'] = True

            return redirect(url_for('main.registration_page_5'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 4: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('registration_page_4.html', form_data=request.form)

    return render_template('registration_page_4.html', form_data={})

@bp.route('/registration_page_5', methods=['GET', 'POST'])
def registration_page_5():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_4_complete'):  # Check for previous page completion
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('main.registration_page_4'))

    if request.method == 'POST':
        try:
            # Educational Records
            education_fields = [
                'uni_serial', 'uni_name', 'uni_year_from', 'uni_year_to',
                'uni_cert', 'uni_grade', 'uni_remarks',
                'sec_serial', 'sec_name', 'sec_year_from', 'sec_year_to',
                'sec_cert', 'sec_grade', 'sec_remarks',
                'mil_serial', 'mil_name', 'mil_year_from', 'mil_year_to',
                'mil_cert', 'mil_grade', 'mil_remarks'
            ]

            # Save all form data to session
            for field in education_fields:
                session[field] = request.form.getlist(f'{field}[]')

            # Save NASS specific information
            session['nass_course'] = request.form.get('nass_course')
            session['nass_department'] = request.form.get('nass_department')

            # Validate required fields
            if not session.get('uni_name')[0]:
                flash('At least one university/polytechnic entry is required', 'error')
                return render_template('registration_page_5.html')

            session['page_5_complete'] = True
            return redirect(url_for('main.registration_page_6'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 5: {str(e)}")
            flash('An error occurred. Please try again.', 'error')

    return render_template('registration_page_5.html')

@bp.route('/registration_page_6', methods=['GET', 'POST'])
def registration_page_6():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_5_complete'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('main.registration_page_5'))

    if request.method == 'POST':
        try:
            # Handle file uploads
            allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
            max_file_size = 2 * 1024 * 1024  # 2MB for images
            max_pdf_size = 5 * 1024 * 1024   # 5MB for PDFs

            # Required files validation
            if 'passport_photo' not in request.files or not request.files['passport_photo'].filename:
                flash('Passport photograph is required', 'error')
                return render_template('registration_page_6.html')

            # Process passport photo
            passport_photo = request.files['passport_photo']
            if not allowed_file(passport_photo.filename, {'jpg', 'jpeg', 'png'}):
                flash('Invalid passport photo format. Please use JPG or PNG', 'error')
                return render_template('registration_page_6.html')

            if len(passport_photo.read()) > max_file_size:
                flash('Passport photo must be less than 2MB', 'error')
                return render_template('registration_page_6.html')
            passport_photo.seek(0)  # Reset file pointer

            # Save form data to session
            session['has_special_needs'] = request.form.get('has_special_needs')
            if session['has_special_needs'] == 'yes':
                session['special_needs_details'] = request.form.get('special_needs_details')

            session['has_medical_conditions'] = request.form.get('has_medical_conditions')
            if session['has_medical_conditions'] == 'yes':
                session['medical_conditions_details'] = request.form.get('medical_conditions_details')

            session['blood_group'] = request.form.get('blood_group')
            session['genotype'] = request.form.get('genotype')

            # Save files to appropriate storage (implement your file storage logic here)
            # Example:
            # save_file(passport_photo, 'passport_photos', session.get('service_number'))

            session['page_6_complete'] = True
            return redirect(url_for('main.registration_page_7'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 6: {str(e)}")
            flash('An error occurred. Please try again.', 'error')

    return render_template('registration_page_6.html')

@bp.route('/registration_page_7', methods=['GET', 'POST'])
def registration_page_7():
    # Check if registration is open
    if not is_registration_open():
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('main.registration'))
    if not session.get('page_6_complete'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('main.registration_page_6'))

    if request.method == 'POST':
        try:
            # Get all session data
            registration_data = {
                # Personal Information (Page 1)
                'service_number': session.get('service_number'),
                'rank': session.get('rank'),
                'surname': session.get('surname'),
                'other_names': session.get('other_names'),
                'date_of_birth': session.get('date_of_birth'),
                'gender': session.get('gender'),

                # Contact Information (Page 2)
                'nationality': session.get('nationality'),
                'marital_status': session.get('marital_status'),
                'state_of_origin': session.get('state_of_origin'),
                'permanent_address': session.get('permanent_address'),

                # Social Media Contact (Page 3)
                'whatsapp': session.get('whatsapp'),
                'facebook': session.get('facebook'),
                'twitter': session.get('twitter'),

                # Next of Kin Information (Page 4)
                'nok_name_1': session.get('nok_name_1'),
                'nok_relationship_1': session.get('nok_relationship_1'),
                'nok_phone_1': session.get('nok_phone_1'),
                'nok_address_1': session.get('nok_address_1'),

                # Military Information (Page 5)
                'military_courses': session.get('military_courses'),
                'current_unit': session.get('current_unit'),
                'date_of_enlistment': session.get('date_of_enlistment'),

                # Medical Information (Page 6)
                'blood_group': session.get('blood_group'),
                'genotype': session.get('genotype'),
                'has_special_needs': session.get('has_special_needs'),
                'special_needs_details': session.get('special_needs_details'),
                'has_medical_conditions': session.get('has_medical_conditions'),
                'medical_conditions_details': session.get('medical_conditions_details'),
            }

            # Validate that all required fields are present
            required_fields = [
                'service_number', 'rank', 'surname', 'other_names',
                'date_of_birth', 'gender', 'nationality', 'state_of_origin',
                'permanent_address', 'whatsapp', 'nok_name_1', 'nok_phone_1',
                'blood_group', 'genotype'
            ]

            missing_fields = [field for field in required_fields if not registration_data.get(field)]

            if missing_fields:
                flash(f'Missing required information: {", ".join(missing_fields)}', 'error')
                return render_template('registration_page_7.html', data=registration_data)

            # If everything is valid, save to database (implement your database logic here)
            # save_registration(registration_data)

            # Clear the session after successful submission
            session.clear()

            # Redirect to success page
            flash('Registration completed successfully!', 'success')
            return redirect(url_for('main.registration_success'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 7: {str(e)}")
            flash('An error occurred during submission. Please try again.', 'error')

    return render_template('registration_page_7.html', data=session)

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
    # Redirect to the new admin login page
    return redirect(url_for('admin.login'))

@bp.route('/admin_dashboard')
def admin_dashboard():
    # Redirect to the new admin dashboard
    return redirect(url_for('admin.index'))

@bp.route('/students')
def student_list():
    # Check if user is logged in with the new admin system
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('student_list.html', students=students)

@bp.route('/logout')
def logout():
    # Clear both old and new admin session variables
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)

    return redirect(url_for('main.index'))








