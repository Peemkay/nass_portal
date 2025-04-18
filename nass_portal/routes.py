from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from .db import get_db
from .registration_utils import is_registration_open, get_registration_status

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename, extensions=None):
    if extensions is None:
        extensions = ALLOWED_EXTENSIONS

    # Debug logging
    current_app.logger.info(f"Checking file: {filename}, extensions: {extensions}")

    if '.' not in filename:
        current_app.logger.warning(f"No extension found in filename: {filename}")
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    result = ext in extensions

    current_app.logger.info(f"File extension: {ext}, allowed: {result}")
    return result

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get current year for footer
    now = datetime.now()

    # Get active announcements
    db = get_db()
    announcements = db.execute(
        'SELECT * FROM announcements WHERE is_active = 1 ORDER BY display_order LIMIT 10'
    ).fetchall()

    # Get courses
    courses = db.execute('SELECT * FROM courses ORDER BY name').fetchall()

    # Get departments
    departments = db.execute(
        'SELECT * FROM departments WHERE is_active = 1 ORDER BY display_order'
    ).fetchall()

    return render_template('index.html', now=now, announcements=announcements, courses=courses, departments=departments)


@bp.route('/clear-session', methods=['GET', 'POST'])
def clear_session():
    """Clear the user's session data"""
    cleared = False

    if request.method == 'POST':
        # Clear the session
        session.clear()
        cleared = True

    return render_template('clear_session.html', cleared=cleared)


@bp.route('/courses/<int:course_id>')
def view_course(course_id):
    """View course details"""
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()

    if course is None:
        flash('Course not found', 'error')
        return redirect(url_for('main.index'))

    # Get related courses (same category and level)
    related_courses = db.execute(
        'SELECT * FROM courses WHERE (category = ? OR level = ?) AND id != ? LIMIT 3',
        (course.category, course.level, course_id)
    ).fetchall()

    return render_template('course_detail.html', course=course, related_courses=related_courses)


@bp.route('/announcement/<int:announcement_id>')
def view_announcement(announcement_id):
    """View a single announcement"""
    # Get the announcement
    db = get_db()
    announcement = db.execute('SELECT * FROM announcements WHERE id = ? AND is_active = 1', (announcement_id,)).fetchone()

    if not announcement:
        flash('Announcement not found', 'error')
        return redirect(url_for('main.index'))

    # Get other recent announcements
    recent_announcements = db.execute(
        'SELECT * FROM announcements WHERE id != ? AND is_active = 1 ORDER BY display_order LIMIT 3',
        (announcement_id,)
    ).fetchall()

    return render_template('announcement_detail.html', announcement=announcement, recent_announcements=recent_announcements)

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
                'corps': request.form.get('corps'),
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
                'corps': 'Corps',
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
                            date_of_birth = ?, gender = ?, corps = ?, current_unit = ?,
                            date_of_commission = ?, years_in_service = ?,
                            passport_photo = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE service_number = ?
                    ''', (
                        form_data['rank'], form_data['surname'],
                        form_data['other_names'], form_data['date_of_birth'],
                        form_data['gender'], form_data['corps'], form_data['current_unit'],
                        form_data['date_of_commission'], form_data['years_in_service'],
                        session['passport_photo'], form_data['service_number']
                    ))
                else:
                    # Insert new record
                    db.execute('''
                        INSERT INTO students (
                            service_number, rank, surname, other_names,
                            date_of_birth, gender, corps, current_unit,
                            date_of_commission, years_in_service,
                            passport_photo, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        form_data['service_number'], form_data['rank'],
                        form_data['surname'], form_data['other_names'],
                        form_data['date_of_birth'], form_data['gender'],
                        form_data['corps'], form_data['current_unit'],
                        form_data['date_of_commission'],
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
                flash('Next of Kin Phone Number is required', 'error')
                return render_template('registration_page_4.html', form_data=request.form)

            # Ensure both fields have the same value for compatibility
            request_form = request.form.copy()  # Make mutable
            if request_form.get('nok_gsm_number_1') and not request_form.get('nok_phone_1'):
                request_form['nok_phone_1'] = request_form['nok_gsm_number_1']
            elif request_form.get('nok_phone_1') and not request_form.get('nok_gsm_number_1'):
                request_form['nok_gsm_number_1'] = request_form['nok_phone_1']

            # Continue with other validations
            for field in required_fields:
                if field != 'nok_gsm_number_1' and not request.form.get(field):  # Skip phone check as we handled it above
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration_page_4.html', form_data=request.form)

            # Save next of kin data
            nok_fields = ['nok_name_1', 'nok_relationship_1', 'nok_address_1', 'nok_gsm_number_1', 'nok_email_1',
                         'nok_name_2', 'nok_relationship_2', 'nok_address_2', 'nok_gsm_number_2', 'nok_email_2']

            for field in nok_fields:
                session[field] = request_form.get(field, '').strip()

            # Ensure both phone field versions are saved for compatibility
            if request_form.get('nok_gsm_number_1'):
                session['nok_phone_1'] = request_form.get('nok_gsm_number_1', '').strip()
            elif request_form.get('nok_phone_1'):
                session['nok_gsm_number_1'] = request_form.get('nok_phone_1', '').strip()
                session['nok_phone_1'] = request_form.get('nok_phone_1', '').strip()

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
            # Educational Records - new field names
            education_fields = [
                # Tertiary education
                'tertiary_name', 'tertiary_start_date', 'tertiary_end_date',
                'tertiary_cert', 'tertiary_grade', 'tertiary_remarks',
                # Secondary education
                'secondary_name', 'secondary_start_date', 'secondary_end_date',
                'secondary_cert', 'secondary_grade', 'secondary_remarks',
                # Military courses
                'military_name', 'military_start_date', 'military_end_date',
                'military_cert', 'military_grade', 'military_remarks'
            ]

            # Save all form data to session
            for field in education_fields:
                session[field] = request.form.getlist(f'{field}[]')
                current_app.logger.debug(f"Saved {field}: {session[field]}")

            # Save NASS specific information
            session['nass_course'] = request.form.get('nass_course')
            session['nass_department'] = request.form.get('nass_department')

            # Validate required fields - at least one tertiary education entry is required
            tertiary_names = session.get('tertiary_name', [])
            has_valid_entry = False

            for name in tertiary_names:
                if name.strip():
                    has_valid_entry = True
                    break

            if not has_valid_entry:
                flash('At least one university/polytechnic entry is required', 'error')
                return render_template('registration_page_5.html')

            # For backward compatibility with existing code
            # Map new field names to old field names
            field_mapping = {
                'tertiary_name': 'uni_name',
                'tertiary_start_date': 'uni_year_from',
                'tertiary_end_date': 'uni_year_to',
                'tertiary_cert': 'uni_cert',
                'tertiary_grade': 'uni_grade',
                'tertiary_remarks': 'uni_remarks',
                'secondary_name': 'sec_name',
                'secondary_start_date': 'sec_year_from',
                'secondary_end_date': 'sec_year_to',
                'secondary_cert': 'sec_cert',
                'secondary_grade': 'sec_grade',
                'secondary_remarks': 'sec_remarks',
                'military_name': 'mil_name',
                'military_start_date': 'mil_year_from',
                'military_end_date': 'mil_year_to',
                'military_cert': 'mil_cert',
                'military_grade': 'mil_grade',
                'military_remarks': 'mil_remarks'
            }

            # Create legacy fields for backward compatibility
            for new_field, old_field in field_mapping.items():
                if session.get(new_field):
                    session[old_field] = session[new_field]

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

    # Get document requirements from database
    db = get_db()
    document_requirements = db.execute('SELECT * FROM document_requirements WHERE is_active = 1 ORDER BY display_order').fetchall()

    if request.method == 'POST':
        try:
            # Handle document uploads

            # Process each document requirement
            uploaded_documents = []

            for req in document_requirements:
                field_name = f'document_{req["id"]}'

                # Check if file was uploaded
                if field_name in request.files and request.files[field_name].filename:
                    document_file = request.files[field_name]

                    # Validate file type
                    allowed_types = set(req['file_types'].split(','))
                    current_app.logger.info(f"Processing document: {req['name']}, file: {document_file.filename}, allowed types: {allowed_types}")

                    if not allowed_file(document_file.filename, allowed_types):
                        flash(f'Invalid file format for {req["name"]}. Allowed formats: {req["file_types"].upper()}', 'error')
                        return render_template('registration_page_6.html', document_requirements=document_requirements)

                    # Validate file size
                    document_file.seek(0, os.SEEK_END)
                    file_size = document_file.tell()
                    document_file.seek(0)  # Reset file pointer

                    if file_size > req['max_file_size']:
                        max_size_mb = req['max_file_size'] / (1024 * 1024)
                        flash(f'{req["name"]} file must be less than {max_size_mb}MB', 'error')
                        return render_template('registration_page_6.html', document_requirements=document_requirements)

                    # Generate unique filename
                    filename = secure_filename(document_file.filename)
                    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    unique_filename = f"{session.get('service_number')}_{req['id']}_{int(time.time())}.{file_ext}"

                    # Save file
                    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, unique_filename)

                    try:
                        current_app.logger.info(f"Saving document to: {file_path}")
                        document_file.save(file_path)
                        current_app.logger.info(f"Document saved successfully")
                    except Exception as e:
                        current_app.logger.error(f"Error saving document: {str(e)}")
                        flash(f'Error saving {req["name"]}: {str(e)}', 'error')
                        return render_template('registration_page_6.html', document_requirements=document_requirements)

                    # Add to uploaded documents list
                    uploaded_documents.append({
                        'requirement_id': req['id'],
                        'file_path': os.path.join('documents', unique_filename),
                        'original_filename': filename,
                        'file_size': file_size,
                        'file_type': file_ext
                    })
                elif req['is_required']:
                    flash(f'{req["name"]} is required', 'error')
                    return render_template('registration_page_6.html', document_requirements=document_requirements)

            # Store uploaded documents in session
            session['uploaded_documents'] = uploaded_documents

            # Save form data to session
            session['has_special_needs'] = request.form.get('has_special_needs')
            if session['has_special_needs'] == 'yes':
                session['special_needs_details'] = request.form.get('special_needs_details')

            session['has_medical_conditions'] = request.form.get('has_medical_conditions')
            if session['has_medical_conditions'] == 'yes':
                session['medical_conditions_details'] = request.form.get('medical_conditions_details')

            session['blood_group'] = request.form.get('blood_group')
            session['genotype'] = request.form.get('genotype')

            session['page_6_complete'] = True
            return redirect(url_for('main.registration_page_7'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 6: {str(e)}")
            flash('An error occurred. Please try again.', 'error')

    return render_template('registration_page_6.html', document_requirements=document_requirements)

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
                'nok_phone_1': session.get('nok_phone_1') or session.get('nok_gsm_number_1'),
                'nok_gsm_number_1': session.get('nok_gsm_number_1') or session.get('nok_phone_1'),
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

            # If everything is valid, save to database
            try:
                db = get_db()

                # Check if service number already exists
                existing_student = db.execute('SELECT id FROM students WHERE service_number = ?',
                                             (registration_data['service_number'],)).fetchone()
                if existing_student:
                    flash('A student with this service number already exists.', 'error')
                    return render_template('registration_page_7.html', data=registration_data)

                # Calculate years in service
                enlistment_date = datetime.strptime(registration_data['date_of_enlistment'], '%Y-%m-%d')
                years_in_service = datetime.now().year - enlistment_date.year

                # Insert into students table
                db.execute(
                    'INSERT INTO students (service_number, rank, surname, other_names, date_of_birth, gender, corps, '
                    'current_unit, date_of_commission, years_in_service, passport_photo) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (registration_data['service_number'], registration_data['rank'],
                     registration_data['surname'], registration_data['other_names'],
                     registration_data['date_of_birth'], registration_data['gender'],
                     registration_data.get('corps', ''), registration_data['current_unit'],
                     registration_data['date_of_enlistment'],
                     years_in_service, session.get('passport_photo', ''))
                )

                # Get the student ID
                student_id = db.execute('SELECT id FROM students WHERE service_number = ?',
                                       (registration_data['service_number'],)).fetchone()['id']

                # Save uploaded documents
                if 'uploaded_documents' in session and session['uploaded_documents']:
                    for doc in session['uploaded_documents']:
                        db.execute(
                            'INSERT INTO student_documents (student_id, requirement_id, file_path, original_filename, '
                            'file_size, file_type) VALUES (?, ?, ?, ?, ?, ?)',
                            (student_id, doc['requirement_id'], doc['file_path'], doc['original_filename'],
                             doc['file_size'], doc['file_type'])
                        )

                db.commit()
                current_app.logger.info(f"Student registered successfully: {registration_data['service_number']}")
            except Exception as e:
                db.rollback()
                current_app.logger.error(f"Database error during registration: {str(e)}")
                flash('An error occurred while saving your registration. Please try again.', 'error')
                return render_template('registration_page_7.html', data=registration_data)

            # Clear the session after successful submission
            session.clear()

            # Redirect to success page
            flash('Registration completed successfully!', 'success')
            return redirect(url_for('main.registration_success'))

        except Exception as e:
            current_app.logger.error(f"Error in registration page 7: {str(e)}")
            flash('An error occurred during submission. Please try again.', 'error')

    return render_template('registration_page_7.html', data=session)

@bp.route('/registration_success')
def registration_success():
    return render_template('success.html')

@bp.route('/courses')
def courses():
    return render_template('courses.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/test-carousel')
def test_carousel():
    return render_template('test_carousel.html')


@bp.route('/simple-contact', methods=['GET', 'POST'])
def simple_contact():
    """A simplified contact form that uses a different approach for sending emails"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Log the form submission
        current_app.logger.info(f"Simple contact form submitted by {name} ({email})")

        # Validate form data
        if not name or not email or not subject or not message:
            flash('Please fill in all fields', 'error')
            return render_template('simple_contact.html')

        try:
            # Get mail settings directly from the database
            from .db import get_db
            db = get_db()

            # Get mail settings
            mail_settings = {}
            settings = db.execute('SELECT setting_key, setting_value, setting_type FROM settings WHERE category = ?', ('mail',)).fetchall()

            for setting in settings:
                key = setting['setting_key']
                value = setting['setting_value']

                # Convert value based on type
                if setting['setting_type'] == 'boolean':
                    value = value.lower() == 'true'
                elif setting['setting_type'] == 'number':
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0

                mail_settings[key] = value

            # Configure Flask-Mail with the settings
            current_app.config['MAIL_SERVER'] = mail_settings.get('mail_server', 'smtp.mail.yahoo.com')
            current_app.config['MAIL_PORT'] = int(mail_settings.get('mail_port', 587))
            current_app.config['MAIL_USE_TLS'] = mail_settings.get('mail_use_tls', True)
            current_app.config['MAIL_USE_SSL'] = mail_settings.get('mail_use_ssl', False)
            current_app.config['MAIL_USERNAME'] = mail_settings.get('mail_username', '')
            current_app.config['MAIL_PASSWORD'] = mail_settings.get('mail_password', '')
            current_app.config['MAIL_DEFAULT_SENDER'] = f"{mail_settings.get('mail_sender_name', 'NASS Portal')} <{mail_settings.get('mail_default_sender', 'noreply@nassportal.mil.ng')}>"

            # Log mail settings (without password)
            safe_settings = {k: v for k, v in current_app.config.items() if k.startswith('MAIL_') and k != 'MAIL_PASSWORD'}
            current_app.logger.info(f"Mail settings: {safe_settings}")

            # Get recipients
            recipients_str = mail_settings.get('mail_contact_form_recipients', '')
            recipients = [e.strip() for e in recipients_str.split(',')] if recipients_str else []

            if not recipients:
                default_sender = mail_settings.get('mail_default_sender', 'noreply@nassportal.mil.ng')
                recipients = [default_sender]

            current_app.logger.info(f"Recipients: {recipients}")

            # Create message
            from flask_mail import Message
            from . import mail

            msg = Message(
                subject=f"{mail_settings.get('mail_contact_form_subject_prefix', '[NASS Portal Contact]')} {subject}",
                recipients=recipients,
                reply_to=email,
                body=f"""From: {name} <{email}>

Subject: {subject}

Message:
{message}
""",
                html=f"""<h3>New Contact Form Submission</h3>
<p><strong>From:</strong> {name} &lt;{email}&gt;</p>
<p><strong>Subject:</strong> {subject}</p>
<p><strong>Message:</strong></p>
<div style="padding: 15px; border-left: 4px solid #ccc; background-color: #f9f9f9;">
    {message.replace('\n', '<br>')}
</div>
<p style="color: #777; font-size: 12px; margin-top: 20px;">
    This message was sent from the NASS Portal simple contact form.
</p>"""
            )

            # Send email
            current_app.logger.info("Attempting to send email")
            mail.send(msg)
            current_app.logger.info("Email sent successfully")

            flash('Thank you for your message. We will get back to you soon!', 'success')
        except Exception as e:
            import traceback
            current_app.logger.error(f"Error sending email: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash(f'An error occurred while sending your message: {str(e)}', 'error')

        return render_template('simple_contact.html')

    return render_template('simple_contact.html')


@bp.route('/direct-contact', methods=['GET', 'POST'])
def direct_contact():
    """A direct contact form that uses smtplib directly"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Log the form submission
        current_app.logger.info(f"Direct contact form submitted by {name} ({email})")

        # Validate form data
        if not name or not email or not subject or not message:
            flash('Please fill in all fields', 'error')
            return render_template('direct_contact.html')

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Yahoo Mail credentials - hardcoded for reliability
            yahoo_email = "chakin700@yahoo.com"
            yahoo_password = "xswwpjaotwholron"  # App password

            # Use a different recipient email to avoid Yahoo's self-sending restrictions
            # You can change this to any email address you want to receive the contact form submissions
            recipient_email = "ariespeemkay@gmail.com"  # Your Gmail address

            # If no recipient is specified, use a default one
            if not recipient_email:
                recipient_email = "nass.portal.contact@gmail.com"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[NASS Portal Contact] {subject}"
            msg['From'] = f"NASS Portal <{yahoo_email}>"
            msg['To'] = recipient_email
            msg['Reply-To'] = email

            # Create plain text and HTML versions of the message
            text_content = f"""From: {name} <{email}>

Subject: {subject}

Message:
{message}
"""

            html_content = f"""<h3>New Contact Form Submission</h3>
<p><strong>From:</strong> {name} &lt;{email}&gt;</p>
<p><strong>Subject:</strong> {subject}</p>
<p><strong>Message:</strong></p>
<div style="padding: 15px; border-left: 4px solid #ccc; background-color: #f9f9f9;">
    {message.replace('\n', '<br>')}
</div>
<p style="color: #777; font-size: 12px; margin-top: 20px;">
    This message was sent from the NASS Portal direct contact form.
</p>"""

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Connect to Yahoo Mail's SMTP server
            current_app.logger.info("Connecting to smtp.mail.yahoo.com:587...")
            server = smtplib.SMTP('smtp.mail.yahoo.com', 587)

            # Start TLS encryption
            current_app.logger.info("Starting TLS...")
            server.starttls()

            # Login to Yahoo Mail
            current_app.logger.info(f"Logging in as {yahoo_email}...")
            server.login(yahoo_email, yahoo_password)

            # Send email
            current_app.logger.info(f"Sending email to {recipient_email}...")
            server.sendmail(yahoo_email, recipient_email, msg.as_string())

            # Close connection
            server.quit()
            current_app.logger.info("Email sent successfully!")

            flash('Thank you for your message. We will get back to you soon!', 'success')
        except Exception as e:
            import traceback
            current_app.logger.error(f"Error sending email: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash(f'An error occurred while sending your message: {str(e)}', 'error')

        return render_template('direct_contact.html')

    return render_template('direct_contact.html')


@bp.route('/brevo-contact', methods=['GET', 'POST'])
def brevo_contact():
    """A contact form that uses Brevo API for sending emails"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Log the form submission
        current_app.logger.info(f"Brevo contact form submitted by {name} ({email})")

        # Validate form data
        if not name or not email or not subject or not message:
            flash('Please fill in all fields', 'error')
            return render_template('brevo_contact.html')

        # Use our Brevo implementation to send the contact form email
        from .brevo_mail import send_contact_form_email
        success, error_message = send_contact_form_email(name, email, subject, message)

        if success:
            flash('Thank you for your message. We will get back to you soon!', 'success')
        else:
            current_app.logger.error(f"Error sending contact form email: {error_message}")
            flash(f'An error occurred while sending your message: {error_message}', 'error')

        return render_template('brevo_contact.html')

    return render_template('brevo_contact.html')


@bp.route('/formsubmit-contact')
def formsubmit_contact():
    """A contact form that uses FormSubmit.co for processing"""
    return render_template('formsubmit_contact.html')


@bp.route('/thank-you')
def thank_you():
    """Thank you page after form submission"""
    flash('Thank you for your message. We will get back to you soon!', 'success')
    return render_template('thank_you.html')


@bp.route('/local-contact', methods=['GET', 'POST'])
def local_contact():
    """A contact form that stores messages in the local database"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Log the form submission
        current_app.logger.info(f"Local contact form submitted by {name} ({email})")

        # Validate form data
        if not name or not email or not subject or not message:
            flash('Please fill in all fields', 'error')
            return render_template('local_contact.html')

        try:
            # Store the message in the database
            from .db import get_db
            db = get_db()

            db.execute(
                'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
                (name, email, subject, message)
            )
            db.commit()

            current_app.logger.info("Contact message stored in database")
            flash('Thank you for your message. We will get back to you soon!', 'success')

        except Exception as e:
            import traceback
            current_app.logger.error(f"Error storing contact message: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash('An error occurred while processing your message. Please try again.', 'error')

        return render_template('local_contact.html')

    return render_template('local_contact.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Log the form submission for debugging
        current_app.logger.info("Contact form submitted")

        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Log the form data for debugging
        current_app.logger.info(f"Form data: name={name}, email={email}, subject={subject}")

        # Validate form data
        if not name or not email or not subject or not message:
            flash('Please fill in all fields', 'error')
            return render_template('contact.html')

        try:
            # Store the message in the database
            from .db import get_db
            db = get_db()

            db.execute(
                'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
                (name, email, subject, message)
            )
            db.commit()

            current_app.logger.info("Contact message stored in database")
            flash('Thank you for your message. We will get back to you soon!', 'success')

        except Exception as e:
            import traceback
            current_app.logger.error(f"Error storing contact message: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash('An error occurred while processing your message. Please try again.', 'error')

        return render_template('contact.html')

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

@bp.route('/maintenance')
def maintenance():
    """Show maintenance page"""
    db = get_db()

    # Get maintenance message and contact information
    message_setting = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_message',)).fetchone()
    maintenance_message = 'The system is currently undergoing scheduled maintenance. Please check back later.'

    if message_setting:
        maintenance_message = message_setting['setting_value']

    # Get contact information
    contact_email = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_contact_email',)).fetchone()
    contact_phone = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_contact_phone',)).fetchone()

    # Get active maintenance details if available
    active_maintenance = db.execute(
        'SELECT * FROM scheduled_maintenance WHERE status = "in_progress" ORDER BY start_datetime LIMIT 1'
    ).fetchone()

    return render_template('maintenance.html',
                          message=maintenance_message,
                          contact_email=contact_email['setting_value'] if contact_email else None,
                          contact_phone=contact_phone['setting_value'] if contact_phone else None,
                          maintenance=active_maintenance)

@bp.route('/enable-maintenance')
def enable_maintenance():
    """Enable maintenance mode - for testing only"""
    db = get_db()

    # Set maintenance mode to true
    db.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('true', 'maintenance_mode'))
    db.commit()

    # Log the action
    current_app.logger.info("Maintenance mode manually enabled")

    # Redirect to maintenance page
    return redirect(url_for('main.maintenance'))

@bp.route('/disable-maintenance')
def disable_maintenance():
    """Disable maintenance mode - for testing only"""
    db = get_db()

    # Set maintenance mode to false
    db.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('false', 'maintenance_mode'))
    db.commit()

    # Log the action
    current_app.logger.info("Maintenance mode manually disabled")

    # Redirect to home page
    return redirect(url_for('main.index'))
