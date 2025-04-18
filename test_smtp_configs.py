"""
Script to test different SMTP configurations
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import time

# Yahoo Mail credentials
YAHOO_EMAIL = "chakin700@yahoo.com"
YAHOO_PASSWORD = "xswwpjaotwholron"  # App password

# Get recipient email from command line or use default
if len(sys.argv) > 1:
    recipient_email = sys.argv[1]
else:
    recipient_email = input("Enter recipient email address: ")

# SMTP configurations to test
smtp_configs = [
    {
        "name": "Yahoo Mail",
        "server": "smtp.mail.yahoo.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False
    },
    {
        "name": "Yahoo Mail (SSL)",
        "server": "smtp.mail.yahoo.com",
        "port": 465,
        "use_tls": False,
        "use_ssl": True
    },
    {
        "name": "Yahoo Mail (Alternative)",
        "server": "smtp.yahoo.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False
    },
    {
        "name": "Yahoo Mail (Alternative SSL)",
        "server": "smtp.yahoo.com",
        "port": 465,
        "use_tls": False,
        "use_ssl": True
    }
]

# Test each configuration
for config in smtp_configs:
    print(f"\n\nTesting configuration: {config['name']}")
    print(f"Server: {config['server']}")
    print(f"Port: {config['port']}")
    print(f"TLS: {config['use_tls']}")
    print(f"SSL: {config['use_ssl']}")
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Test Email from NASS Portal ({config['name']})"
    msg['From'] = f"NASS Portal <{YAHOO_EMAIL}>"
    msg['To'] = recipient_email
    
    # Create content
    text_content = f"This is a test email sent using {config['name']} configuration."
    html_content = f"""
    <html>
    <body>
        <h2>Test Email from NASS Portal</h2>
        <p>This is a test email sent using {config['name']} configuration.</p>
        <p>If you're seeing this, the email configuration is working correctly!</p>
    </body>
    </html>
    """
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        # Connect to SMTP server
        print(f"Connecting to {config['server']}:{config['port']}...")
        
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['server'], config['port'])
        else:
            server = smtplib.SMTP(config['server'], config['port'])
        
        server.set_debuglevel(1)  # Show all communication with the server
        
        # Start TLS if required
        if config['use_tls']:
            print("Starting TLS...")
            server.starttls()
        
        # Login
        print(f"Logging in as {YAHOO_EMAIL}...")
        server.login(YAHOO_EMAIL, YAHOO_PASSWORD)
        
        # Send email
        print(f"Sending email to {recipient_email}...")
        server.sendmail(YAHOO_EMAIL, recipient_email, msg.as_string())
        
        # Close connection
        server.quit()
        print(f"✅ Email sent successfully using {config['name']}!")
        
    except Exception as e:
        print(f"❌ Error with {config['name']}: {str(e)}")
    
    # Wait a bit between attempts
    time.sleep(2)

print("\nTesting complete!")
