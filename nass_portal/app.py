from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"  # Change this to a strong, random key

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your mail server
app.config['MAIL_PORT'] = 587  # Replace with your mail port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'  # Replace with your email

mail = Mail(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    msg = Message(subject=f"Contact Form Submission from {name}",
                  recipients=["recipient@example.com"],  # Replace with the recipient's email
                  body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
    
    mail.send(msg)
    return redirect(url_for('home'))  # Redirect to home after sending

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        db = get_db()
        try:
            db.execute('INSERT INTO courses (name, description) VALUES (?, ?)', (course_name, course_description))
            db.commit()
            return redirect(url_for('courses'))  # Redirect to the courses page on success
        except sqlite3.Error as e:
            error_message = f"Database error: {e}"
            return render_template('add_course.html', error=error_message)
    return render_template('add_course.html')
