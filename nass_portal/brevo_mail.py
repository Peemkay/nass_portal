"""
Email sending functionality using Brevo (formerly Sendinblue) API
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app
import traceback

# Default API key - replace with your actual Brevo API key
DEFAULT_API_KEY = "YOUR_BREVO_API_KEY"

def send_contact_form_email(name, email, subject, message):
    """
    Send an email notification for a contact form submission using Brevo API

    Args:
        name (str): The name of the person submitting the form
        email (str): The email address of the person submitting the form
        subject (str): The subject of the message
        message (str): The message content

    Returns:
        tuple: (success, error_message)
    """
    try:
        # Get API key from app config or use default
        api_key = current_app.config.get('BREVO_API_KEY', DEFAULT_API_KEY)

        # Configure the API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = api_key

        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Get recipient email from app config or use default
        recipient_email = current_app.config.get('CONTACT_FORM_RECIPIENT', 'ariespeemkay@gmail.com')

        # Create a send email object
        sender = {"name": "NASS Portal", "email": "noreply@nassportal.mil.ng"}
        to = [{"email": recipient_email, "name": "NASS Portal Admin"}]

        # Format the email subject
        email_subject = f"[NASS Portal Contact] {subject}"

        # Create HTML content
        html_content = f"""
        <h3>New Contact Form Submission</h3>
        <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <div style="padding: 15px; border-left: 4px solid #ccc; background-color: #f9f9f9;">
            {message.replace('\\n', '<br>')}
        </div>
        <p style="color: #777; font-size: 12px; margin-top: 20px;">
            This message was sent from the NASS Portal contact form.
        </p>
        """

        # Create plain text content
        text_content = f"""
        From: {name} <{email}>

        Subject: {subject}

        Message:
        {message}
        """

        # Create the email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject=email_subject,
            html_content=html_content,
            text_content=text_content,
            reply_to={"email": email, "name": name}
        )

        # Log the email details
        current_app.logger.info(f"Sending contact form email to {recipient_email}")

        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)

        # Log success
        current_app.logger.info(f"Email sent successfully! Message ID: {api_response.message_id}")

        return True, None

    except ApiException as e:
        error_message = f"API error: {e}"
        current_app.logger.error(error_message)
        return False, error_message

    except Exception as e:
        error_message = str(e)
        current_app.logger.error(f"Error sending email: {error_message}")
        current_app.logger.error(traceback.format_exc())
        return False, error_message
