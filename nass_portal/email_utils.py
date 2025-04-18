"""
Email utility functions for the NASS Portal
"""

from flask import current_app
from flask_mail import Message
from . import mail
from .settings_utils import get_setting
import logging

def send_contact_form_email(name, email, subject, message):
    """
    Send an email notification for a contact form submission

    Args:
        name (str): The name of the person submitting the form
        email (str): The email address of the person submitting the form
        subject (str): The subject of the message
        message (str): The message content

    Returns:
        tuple: (success, error_message)
    """
    try:
        # Log the start of the function for debugging
        current_app.logger.info(f"=== CONTACT FORM SUBMISSION ===\nName: {name}\nEmail: {email}\nSubject: {subject}")

        # Check if contact form notifications are enabled
        mail_enabled = get_setting('mail_contact_form_enabled', True)
        current_app.logger.info(f"Contact form notifications enabled: {mail_enabled}")
        if not mail_enabled:
            current_app.logger.info("Contact form notifications are disabled")
            return True, None

        # Get recipients from settings
        recipients_str = get_setting('mail_contact_form_recipients', '')
        current_app.logger.info(f"Recipients string from settings: '{recipients_str}'")
        recipients = [email.strip() for email in recipients_str.split(',')] if recipients_str else []

        # If no recipients are configured, use the default sender
        if not recipients:
            default_sender = get_setting('mail_default_sender', 'noreply@nassportal.mil.ng')
            current_app.logger.info(f"No recipients configured, using default sender: {default_sender}")
            recipients = [default_sender]

        current_app.logger.info(f"Final recipients list: {recipients}")

        # Get subject prefix from settings
        subject_prefix = get_setting('mail_contact_form_subject_prefix', '[NASS Portal Contact]')
        current_app.logger.info(f"Subject prefix: {subject_prefix}")

        # Log mail settings for debugging
        current_app.logger.info("Getting mail settings from database")

        # Update mail configuration with current settings
        mail_settings = {
            'MAIL_SERVER': get_setting('mail_server', 'smtp.gmail.com'),
            'MAIL_PORT': int(get_setting('mail_port', 587)),
            'MAIL_USE_TLS': get_setting('mail_use_tls', True),
            'MAIL_USE_SSL': get_setting('mail_use_ssl', False),
            'MAIL_USERNAME': get_setting('mail_username', ''),
            'MAIL_PASSWORD': get_setting('mail_password', ''),
            'MAIL_DEFAULT_SENDER': f"{get_setting('mail_sender_name', 'NASS Portal')} <{get_setting('mail_default_sender', 'noreply@nassportal.mil.ng')}>"
        }

        # Log mail settings for debugging (without password)
        safe_settings = {k: v for k, v in mail_settings.items() if k != 'MAIL_PASSWORD'}
        current_app.logger.info(f"Mail settings: {safe_settings}")

        # Update mail configuration
        for key, value in mail_settings.items():
            current_app.config[key] = value

        current_app.logger.info("Mail configuration updated")

        # Create email message
        current_app.logger.info(f"Creating email message with recipients: {recipients}")
        msg = Message(
            subject=f"{subject_prefix} {subject}",
            recipients=recipients,
            reply_to=email,
            body=f"""
            From: {name} <{email}>

            Subject: {subject}

            Message:
            {message}
            """,
            html=f"""
            <h3>New Contact Form Submission</h3>
            <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong></p>
            <div style="padding: 15px; border-left: 4px solid #ccc; background-color: #f9f9f9;">
                {message.replace('\n', '<br>')}
            </div>
            <p style="color: #777; font-size: 12px; margin-top: 20px;">
                This message was sent from the NASS Portal contact form.
            </p>
            """
        )

        # Send email
        current_app.logger.info("Attempting to send email")
        try:
            mail.send(msg)
            current_app.logger.info("Contact form email sent successfully")
            return True, None
        except Exception as mail_error:
            current_app.logger.error(f"Error in mail.send(): {str(mail_error)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False, str(mail_error)

    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in send_contact_form_email: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False, str(e)

def send_test_email(recipient):
    """
    Send a test email to verify mail settings

    Args:
        recipient (str): The email address to send the test email to

    Returns:
        tuple: (success, error_message)
    """
    try:
        # Log the start of the function for debugging
        current_app.logger.info(f"=== SENDING TEST EMAIL ===\nRecipient: {recipient}")

        # Update mail configuration with current settings
        mail_settings = {
            'MAIL_SERVER': get_setting('mail_server', 'smtp.gmail.com'),
            'MAIL_PORT': int(get_setting('mail_port', 587)),
            'MAIL_USE_TLS': get_setting('mail_use_tls', True),
            'MAIL_USE_SSL': get_setting('mail_use_ssl', False),
            'MAIL_USERNAME': get_setting('mail_username', ''),
            'MAIL_PASSWORD': get_setting('mail_password', ''),
            'MAIL_DEFAULT_SENDER': f"{get_setting('mail_sender_name', 'NASS Portal')} <{get_setting('mail_default_sender', 'noreply@nassportal.mil.ng')}>"
        }

        # Log mail settings for debugging (without password)
        safe_settings = {k: v for k, v in mail_settings.items() if k != 'MAIL_PASSWORD'}
        current_app.logger.info(f"Mail settings: {safe_settings}")

        # Update mail configuration
        for key, value in mail_settings.items():
            current_app.config[key] = value

        current_app.logger.info("Mail configuration updated")

        # Create email message
        current_app.logger.info(f"Creating test email message for recipient: {recipient}")
        msg = Message(
            subject="NASS Portal - Test Email",
            recipients=[recipient],
            body="This is a test email from the NASS Portal admin panel. If you're receiving this, your mail settings are configured correctly.",
            html="<h1>NASS Portal Test Email</h1><p>This is a test email from the NASS Portal admin panel.</p><p>If you're receiving this, your mail settings are configured correctly.</p>"
        )

        # Send email
        current_app.logger.info("Attempting to send test email")
        try:
            mail.send(msg)
            current_app.logger.info("Test email sent successfully")
            return True, None
        except Exception as mail_error:
            current_app.logger.error(f"Error in mail.send() for test email: {str(mail_error)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False, str(mail_error)

    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in send_test_email: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False, str(e)
