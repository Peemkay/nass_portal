"""
Script to test sending email using Brevo (formerly Sendinblue) API
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import sys

# Configure API key authorization
API_KEY = "YOUR_BREVO_API_KEY"  # Replace with your Brevo API key

# Get recipient email from command line or use default
if len(sys.argv) > 1:
    recipient_email = sys.argv[1]
else:
    recipient_email = input("Enter recipient email address: ")

# Configure the API client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = API_KEY

# Create an instance of the API class
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Create a send email object
sender = {"name": "NASS Portal", "email": "chakin700@yahoo.com"}
to = [{"email": recipient_email, "name": "Recipient"}]
subject = "Test Email from NASS Portal via Brevo API"
html_content = """
<html>
<body>
    <h2>Test Email from NASS Portal</h2>
    <p>This is a test email sent using Brevo API.</p>
    <p>If you're seeing this, the email configuration is working correctly!</p>
</body>
</html>
"""
text_content = "This is a test email sent using Brevo API."

send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
    sender=sender,
    to=to,
    subject=subject,
    html_content=html_content,
    text_content=text_content,
    reply_to={"email": "chakin700@yahoo.com", "name": "NASS Portal"}
)

try:
    # Send the email
    print(f"Sending test email from {sender['email']} to {recipient_email} via Brevo API...")
    api_response = api_instance.send_transac_email(send_smtp_email)
    print(f"Email sent successfully! Message ID: {api_response.message_id}")
    
except ApiException as e:
    print(f"Error sending email: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
