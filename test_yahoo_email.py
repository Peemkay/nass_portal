"""
Test script to send email directly using smtplib with Yahoo Mail
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Yahoo Mail credentials
YAHOO_EMAIL = "chakin700@yahoo.com"
YAHOO_PASSWORD = "xswwpjaotwholron"  # App password

# Email details
recipient_email = YAHOO_EMAIL  # Sending to yourself for testing
subject = "Test Email from NASS Portal"
message_text = "This is a test email sent directly using smtplib."
message_html = """
<html>
<body>
    <h2>Test Email from NASS Portal</h2>
    <p>This is a test email sent directly using smtplib.</p>
    <p>If you're seeing this, the email configuration is working correctly!</p>
</body>
</html>
"""

# Create message
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = YAHOO_EMAIL
msg['To'] = recipient_email

# Attach both plain text and HTML versions
part1 = MIMEText(message_text, 'plain')
part2 = MIMEText(message_html, 'html')
msg.attach(part1)
msg.attach(part2)

try:
    # Connect to Yahoo Mail's SMTP server
    print(f"Connecting to smtp.mail.yahoo.com:587...")
    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server.set_debuglevel(1)  # Show all communication with the server
    
    # Start TLS encryption
    print("Starting TLS...")
    server.starttls()
    
    # Login to Yahoo Mail
    print(f"Logging in as {YAHOO_EMAIL}...")
    server.login(YAHOO_EMAIL, YAHOO_PASSWORD)
    
    # Send email
    print(f"Sending email to {recipient_email}...")
    server.sendmail(YAHOO_EMAIL, recipient_email, msg.as_string())
    
    # Close connection
    server.quit()
    print("Email sent successfully!")
    
except Exception as e:
    print(f"Error sending email: {str(e)}")
