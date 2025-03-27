from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import os

registration_bp = Blueprint('registration', __name__, url_prefix='/registration')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@registration_bp.route('/', methods=['GET'])
def start():
    session.clear()
    return render_template('registration/start.html')

@registration_bp.route('/page-1', methods=['GET', 'POST'])
def page_1():
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = [
                'personnel_number', 'rank', 'name', 'unit', 'dob', 
                'year_in_rank', 'year_of_last_promotion', 'nationality',
                'marital_status', 'permanent_address'
            ]
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration/page_1.html')
            
            # Handle passport photo upload
            if 'passport' not in request.files:
                flash('Passport photograph is required', 'error')
                return render_template('registration/page_1.html')
                
            passport = request.files['passport']
            if passport.filename == '':
                flash('No selected file', 'error')
                return render_template('registration/page_1.html')
                
            if passport and allowed_file(passport.filename):
                filename = secure_filename(f"{request.form['personnel_number']}_{passport.filename}")
                passport.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                session['passport_photo'] = filename
            else:
                flash('Invalid file type. Please upload PNG, JPG or JPEG', 'error')
                return render_template('registration/page_1.html')
            
            # Save form data to session
            for field in required_fields:
                session[field] = request.form[field]
            
            return redirect(url_for('registration.page_2'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 1: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_1.html')

@registration_bp.route('/page-2', methods=['GET', 'POST'])
def page_2():
    if not session.get('personnel_number'):
        flash('Please start from the beginning', 'error')
        return redirect(url_for('registration.page_1'))
    
    if request.method == 'POST':
        try:
            # Save social media data
            social_fields = ['facebook', 'twitter', 'whatsapp', 'instagram']
            
            # Validate WhatsApp as it's required
            if not request.form.get('whatsapp'):
                flash('WhatsApp number is required', 'error')
                return render_template('registration/page_2.html')
            
            # Save social media data to session
            for field in social_fields:
                session[field] = request.form.get(field, '')
            
            return redirect(url_for('registration.page_3'))
        except Exception as e:
            current_app.logger.error(f"Error in registration page 2: {str(e)}")
            flash('An error occurred', 'error')
            
    return render_template('registration/page_2.html')

@registration_bp.route('/page-3', methods=['GET', 'POST'])
def page_3():
    if not session.get('whatsapp'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration.page_2'))
    
    if request.method == 'POST':
        try:
            # Validate and save educational background
            required_fields = ['highest_qualification', 'institution', 'year_completed']
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration/page_3.html')
            
            # Save educational data to session
            for field in required_fields:
                session[field] = request.form[field]
            
            return redirect(url_for('registration.page_4'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 3: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_3.html')

@registration_bp.route('/page-4', methods=['GET', 'POST'])
def page_4():
    if not session.get('highest_qualification'):  # Check for page 3 completion
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration.page_3'))
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['nok_name_1', 'nok_address_1', 'nok_gsm_number_1']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration/page_4.html')
            
            # Save next of kin data
            session['nok_name_1'] = request.form['nok_name_1']
            session['nok_address_1'] = request.form['nok_address_1']
            session['nok_gsm_number_1'] = request.form['nok_gsm_number_1']
            session['nok_email_1'] = request.form.get('nok_email_1', '')  # Optional field
            
            # Add a completion flag for page 4
            session['page_4_complete'] = True
            
            return redirect(url_for('registration.page_5'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 4: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_4.html')

@registration_bp.route('/page-5', methods=['GET', 'POST'])
def page_5():
    # Check both for specific data and completion flag
    if not session.get('page_4_complete') or not session.get('nok_name_1'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration.page_4'))
    
    if request.method == 'POST':
        try:
            # Validate and save military training data
            required_fields = ['military_courses', 'date_commissioned', 'service_number']
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration/page_5.html')
            
            # Save military training data to session
            for field in required_fields:
                session[field] = request.form[field]
            
            # Add a completion flag for page 5
            session['page_5_complete'] = True
            
            return redirect(url_for('registration.page_6'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 5: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_5.html')

@registration_bp.route('/page-6', methods=['GET', 'POST'])
def page_6():
    if not session.get('military_courses'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration.page_5'))
    
    if request.method == 'POST':
        try:
            # Validate and save medical information
            required_fields = ['blood_group', 'genotype', 'allergies']
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('registration/page_6.html')
            
            # Save medical data to session
            for field in required_fields:
                session[field] = request.form[field]
            
            return redirect(url_for('registration.page_7'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 6: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_6.html')

@registration_bp.route('/page-7', methods=['GET', 'POST'])
def page_7():
    if not session.get('blood_group'):
        flash('Please complete previous steps first', 'error')
        return redirect(url_for('registration.page_6'))
    
    if request.method == 'POST':
        try:
            # Final submission
            return redirect(url_for('registration.submit'))
            
        except Exception as e:
            current_app.logger.error(f"Error in registration page 7: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('registration/page_7.html')

@registration_bp.route('/submit', methods=['POST'])
def submit():
    try:
        # Here you would implement the logic to save all session data to your database
        # After successful save, clear the session
        session.clear()
        return redirect(url_for('registration.success'))
    except Exception as e:
        current_app.logger.error(f"Error in registration submission: {str(e)}")
        flash('Registration submission failed', 'error')
        return redirect(url_for('registration.page_7'))

@registration_bp.route('/success')
def success():
    return render_template('registration/success.html')


