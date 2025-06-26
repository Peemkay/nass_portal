from flask import current_app, render_template
from flask_mail import Message
from datetime import datetime
from . import mail
import os

def send_registration_complete_email(student, course):
    """Send registration complete email to student"""
    try:
        msg = Message(
            subject="Registration Complete - Nigerian Army School of Signals",
            recipients=[student['email']],
            html=render_template(
                'emails/registration_complete.html',
                student=student,
                course=course,
                current_year=datetime.now().year
            )
        )
        
        # Attach logo
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'na_logo.png')
        with open(logo_path, 'rb') as logo_file:
            msg.attach(
                filename='na_logo.png',
                content_type='image/png',
                data=logo_file.read(),
                disposition='inline',
                headers=[['Content-ID', '<logo>']]
            )
        
        mail.send(msg)
        current_app.logger.info(f"Registration complete email sent to {student['email']}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending registration complete email: {str(e)}")
        return False

def send_course_registration_email(student, course):
    """Send course registration email to student"""
    try:
        msg = Message(
            subject=f"Course Registration Confirmation - {course['name']}",
            recipients=[student['email']],
            html=render_template(
                'emails/course_registration.html',
                student=student,
                course=course,
                current_year=datetime.now().year
            )
        )
        
        # Attach logo
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'na_logo.png')
        with open(logo_path, 'rb') as logo_file:
            msg.attach(
                filename='na_logo.png',
                content_type='image/png',
                data=logo_file.read(),
                disposition='inline',
                headers=[['Content-ID', '<logo>']]
            )
        
        mail.send(msg)
        current_app.logger.info(f"Course registration email sent to {student['email']}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending course registration email: {str(e)}")
        return False

def send_certificate_issued_email(student, course, certificate):
    """Send certificate issued email to student"""
    try:
        msg = Message(
            subject=f"Certificate Issued - {course['name']}",
            recipients=[student['email']],
            html=render_template(
                'emails/certificate_issued.html',
                student=student,
                course=course,
                certificate=certificate,
                current_year=datetime.now().year
            )
        )
        
        # Attach logo
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'na_logo.png')
        with open(logo_path, 'rb') as logo_file:
            msg.attach(
                filename='na_logo.png',
                content_type='image/png',
                data=logo_file.read(),
                disposition='inline',
                headers=[['Content-ID', '<logo>']]
            )
        
        mail.send(msg)
        current_app.logger.info(f"Certificate issued email sent to {student['email']}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending certificate issued email: {str(e)}")
        return False
