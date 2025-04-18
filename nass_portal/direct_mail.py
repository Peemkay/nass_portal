"""
Direct mail sending functionality using smtplib
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import traceback

def send_email(sender_email, sender_name, recipient_emails, subject, text_content, html_content, reply_to=None):
    """
    Send an email using smtplib directly
    
    Args:
        sender_email (str): The sender's email address
        sender_name (str): The sender's name
        recipient_emails (list): List of recipient email addresses
        subject (str): Email subject
        text_content (str): Plain text content
        html_content (str): HTML content
        reply_to (str, optional): Reply-to email address
        
    Returns:
        tuple: (success, error_message)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = ", ".join(recipient_emails)
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Get mail settings from app config
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.mail.yahoo.com')
        mail_port = int(current_app.config.get('MAIL_PORT', 587))
        mail_username = current_app.config.get('MAIL_USERNAME', '')
        mail_password = current_app.config.get('MAIL_PASSWORD', '')
        use_tls = current_app.config.get('MAIL_USE_TLS', True)
        
        current_app.logger.debug(f"Mail settings: server={mail_server}, port={mail_port}, username={mail_username}, use_tls={use_tls}")
        
        # Connect to SMTP server
        current_app.logger.debug(f"Connecting to {mail_server}:{mail_port}...")
        server = smtplib.SMTP(mail_server, mail_port)
        
        # Start TLS if required
        if use_tls:
            current_app.logger.debug("Starting TLS...")
            server.starttls()
        
        # Login
        current_app.logger.debug(f"Logging in as {mail_username}...")
        server.login(mail_username, mail_password)
        
        # Send email
        current_app.logger.debug(f"Sending email to {recipient_emails}...")
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        
        # Close connection
        server.quit()
        current_app.logger.info("Email sent successfully!")
        
        return True, None
        
    except Exception as e:
        error_message = str(e)
        current_app.logger.error(f"Error sending email: {error_message}")
        current_app.logger.error(traceback.format_exc())
        return False, error_message

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
    from .db import get_db
    
    try:
        # Get mail settings from database
        db = get_db()
        settings = db.execute('SELECT setting_key, setting_value, setting_type FROM settings WHERE category = ?', ('mail',)).fetchall()
        
        mail_settings = {}
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
        
        # Update app config with mail settings
        current_app.config['MAIL_SERVER'] = mail_settings.get('mail_server', 'smtp.mail.yahoo.com')
        current_app.config['MAIL_PORT'] = int(mail_settings.get('mail_port', 587))
        current_app.config['MAIL_USE_TLS'] = mail_settings.get('mail_use_tls', True)
        current_app.config['MAIL_USE_SSL'] = mail_settings.get('mail_use_ssl', False)
        current_app.config['MAIL_USERNAME'] = mail_settings.get('mail_username', '')
        current_app.config['MAIL_PASSWORD'] = mail_settings.get('mail_password', '')
        
        # Get sender information
        sender_email = mail_settings.get('mail_username', '')
        sender_name = mail_settings.get('mail_sender_name', 'NASS Portal')
        
        # Get recipients
        recipients_str = mail_settings.get('mail_contact_form_recipients', '')
        recipients = [e.strip() for e in recipients_str.split(',')] if recipients_str else []
        
        if not recipients:
            recipients = [sender_email]
        
        # Get subject prefix
        subject_prefix = mail_settings.get('mail_contact_form_subject_prefix', '[NASS Portal Contact]')
        full_subject = f"{subject_prefix} {subject}"
        
        # Create email content
        text_content = f"""
From: {name} <{email}>

Subject: {subject}

Message:
{message}
"""

        html_content = f"""
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
        
        # Send email
        return send_email(
            sender_email=sender_email,
            sender_name=sender_name,
            recipient_emails=recipients,
            subject=full_subject,
            text_content=text_content,
            html_content=html_content,
            reply_to=email
        )
        
    except Exception as e:
        error_message = str(e)
        current_app.logger.error(f"Error preparing contact form email: {error_message}")
        current_app.logger.error(traceback.format_exc())
        return False, error_message
