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

print("Starting email test with Yahoo Mail...")
print(f"From: {YAHOO_EMAIL}")
print(f"To: {recipient_email}")
print(f"Subject: {subject}")

try:
    # Connect to Yahoo Mail's SMTP server
    print(f"\nStep 1: Connecting to smtp.mail.yahoo.com:587...")
    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server.set_debuglevel(1)  # Show all communication with the server
    print("Connection established.")

    # Start TLS encryption
    print("\nStep 2: Starting TLS...")
    server.starttls()
    print("TLS started.")

    # Login to Yahoo Mail
    print(f"\nStep 3: Logging in as {YAHOO_EMAIL}...")
    server.login(YAHOO_EMAIL, YAHOO_PASSWORD)
    print("Login successful.")

    # Send email
    print(f"\nStep 4: Sending email to {recipient_email}...")
    server.sendmail(YAHOO_EMAIL, recipient_email, msg.as_string())
    print("Email sent.")

    # Close connection
    print("\nStep 5: Closing connection...")
    server.quit()
    print("Connection closed.")

    print("\n✅ Email sent successfully!")

except Exception as e:
    print(f"\n❌ Error sending email: {str(e)}")
    import traceback
    print("\nDetailed error information:")
    traceback.print_exc()
