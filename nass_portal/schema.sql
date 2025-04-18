DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS registration_periods;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS document_requirements;
DROP TABLE IF EXISTS student_documents;
DROP TABLE IF EXISTS education_records;
DROP TABLE IF EXISTS secondary_education;
DROP TABLE IF EXISTS military_courses;
DROP TABLE IF EXISTS contact_messages;

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_number TEXT NOT NULL,
    rank TEXT NOT NULL,
    surname TEXT NOT NULL,
    other_names TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT NOT NULL,
    corps TEXT,
    current_unit TEXT NOT NULL,
    date_of_commission TEXT NOT NULL,
    years_in_service INTEGER NOT NULL,
    passport_photo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    duration TEXT,
    category TEXT DEFAULT 'General',
    level TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_students_service_number ON students(service_number);
CREATE INDEX IF NOT EXISTS idx_students_surname ON students(surname);
CREATE INDEX IF NOT EXISTS idx_students_rank ON students(rank);
CREATE INDEX IF NOT EXISTS idx_students_current_unit ON students(current_unit);

-- Create registration_periods table for managing registration deadlines
CREATE TABLE IF NOT EXISTS registration_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quarter TEXT NOT NULL,  -- 'first', 'second', 'third'
    year INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Insert default registration periods
INSERT INTO registration_periods (quarter, year, start_date, end_date, is_active, description)
VALUES
('first', 2025, '2025-01-01', '2025-04-30', 1, 'First Quarter Registration Period'),
('second', 2025, '2025-05-01', '2025-08-31', 0, 'Second Quarter Registration Period'),
('third', 2025, '2025-09-01', '2025-12-31', 0, 'Third Quarter Registration Period');

-- Create announcements table for managing homepage announcements
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Insert default announcements
INSERT INTO announcements (title, content, is_active, display_order)
VALUES
('Q2 Course Registration Open', 'Registration for the second quarter courses is now open. Apply before the deadline to secure your spot.', 1, 1),
('New Advanced Cybersecurity Course', 'We are introducing a new advanced cybersecurity course for officers starting next quarter.', 1, 2),
('Graduation Ceremony', 'The graduation ceremony for Q1 courses will be held on May 5th, 2025 at the main parade ground.', 1, 3);

-- Create settings table for system-wide configuration
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type TEXT NOT NULL,  -- 'text', 'number', 'boolean', 'json', etc.
    category TEXT NOT NULL,      -- 'general', 'registration', 'email', 'security', etc.
    description TEXT,
    is_public BOOLEAN NOT NULL DEFAULT 0,  -- Whether this setting can be exposed to public pages
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Insert default settings
INSERT INTO settings (setting_key, setting_value, setting_type, category, description, is_public)
VALUES
-- General Settings
('site_title', 'Nigerian Army School of Signals Portal', 'text', 'general', 'The title of the website', 1),
('site_description', 'Official portal for the Nigerian Army School of Signals', 'text', 'general', 'Meta description for the website', 1),
('contact_email', 'contact@nassportal.mil.ng', 'text', 'general', 'Primary contact email address', 1),
('contact_phone', '+234 123 456 7890', 'text', 'general', 'Primary contact phone number', 1),
('footer_text', '© Nigerian Army School of Signals. All rights reserved.', 'text', 'general', 'Text displayed in the footer', 1),

-- Mail Settings
('mail_server', 'smtp.gmail.com', 'text', 'mail', 'SMTP server address', 0),
('mail_port', '587', 'number', 'mail', 'SMTP server port', 0),
('mail_use_tls', 'true', 'boolean', 'mail', 'Use TLS encryption', 0),
('mail_use_ssl', 'false', 'boolean', 'mail', 'Use SSL encryption', 0),
('mail_username', '', 'text', 'mail', 'SMTP username/email', 0),
('mail_password', '', 'text', 'mail', 'SMTP password or app password', 0),
('mail_default_sender', 'noreply@nassportal.mil.ng', 'text', 'mail', 'Default sender email address', 0),
('mail_sender_name', 'NASS Portal', 'text', 'mail', 'Sender name for outgoing emails', 0),
('mail_contact_form_enabled', 'true', 'boolean', 'mail', 'Enable email notifications for contact form submissions', 0),
('mail_contact_form_recipients', '', 'text', 'mail', 'Comma-separated list of email addresses to receive contact form submissions', 0),
('mail_contact_form_subject_prefix', '[NASS Portal Contact]', 'text', 'mail', 'Subject prefix for contact form emails', 0),

-- Registration Settings
('max_students_per_course', '50', 'number', 'registration', 'Maximum number of students allowed per course', 0),
('require_approval', 'true', 'boolean', 'registration', 'Whether registrations require admin approval', 0),
('registration_email_notification', 'true', 'boolean', 'registration', 'Send email notifications for new registrations', 0),
('registration_closed_message', 'Registration is currently closed. Please check back during the next registration period.', 'text', 'registration', 'Message shown when registration is closed', 1),

-- Security Settings
('password_min_length', '8', 'number', 'security', 'Minimum password length', 0),
('session_timeout', '3600', 'number', 'security', 'Session timeout in seconds', 0),
('login_attempts', '5', 'number', 'security', 'Maximum failed login attempts before lockout', 0),
('lockout_duration', '1800', 'number', 'security', 'Account lockout duration in seconds', 0),

-- System Settings
('maintenance_mode', 'false', 'boolean', 'system', 'Whether the site is in maintenance mode', 0),
('maintenance_message', 'The system is currently undergoing scheduled maintenance. Please check back later.', 'text', 'system', 'Message shown during maintenance mode', 1),
('debug_mode', 'false', 'boolean', 'system', 'Whether debug mode is enabled', 0),
('log_level', 'error', 'text', 'system', 'Logging level (debug, info, warning, error)', 0);

-- Create document requirements table
CREATE TABLE IF NOT EXISTS document_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_required BOOLEAN NOT NULL DEFAULT 1,
    file_types TEXT NOT NULL DEFAULT 'pdf,jpg,jpeg,png',  -- Comma-separated list of allowed file extensions
    max_file_size INTEGER NOT NULL DEFAULT 5242880,  -- Default 5MB in bytes
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create student documents table
CREATE TABLE IF NOT EXISTS student_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    requirement_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES document_requirements (id) ON DELETE CASCADE
);

-- Insert default document requirements
INSERT INTO document_requirements (name, description, is_required, file_types, display_order)
VALUES
('Birth Certificate', 'Official birth certificate or age declaration', 1, 'pdf,jpg,jpeg,png', 1),
('Educational Certificate', 'Highest educational qualification certificate', 1, 'pdf,jpg,jpeg,png', 2),
('Military ID Card', 'Front and back of your military ID card', 1, 'pdf,jpg,jpeg,png', 3),
('Posting Letter', 'Current posting letter to your unit', 1, 'pdf', 4),
('Medical Certificate', 'Recent medical fitness certificate', 0, 'pdf', 5);

-- Create education records table for tertiary education
CREATE TABLE IF NOT EXISTS education_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    serial_number TEXT,
    institution_name TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- YYYY-MM format
    end_date TEXT NOT NULL,    -- YYYY-MM format
    certificate TEXT NOT NULL,
    grade TEXT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Create secondary education table
CREATE TABLE IF NOT EXISTS secondary_education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    serial_number TEXT,
    institution_name TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- YYYY-MM format
    end_date TEXT NOT NULL,    -- YYYY-MM format
    certificate TEXT NOT NULL,
    grade TEXT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Create military courses table
CREATE TABLE IF NOT EXISTS military_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    serial_number TEXT,
    institution_name TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- YYYY-MM format
    end_date TEXT NOT NULL,    -- YYYY-MM format
    certificate TEXT NOT NULL,
    grade TEXT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Create contact messages table
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user with hashed password (password: admin123)
INSERT INTO admins (username, password)
VALUES ('admin', 'pbkdf2:sha256:150000$LnrTXNNj$d119fae74dc2817dd7c3c5bd9a27ebf2c1a7a5b237b0ecdd2c2a1e906c4c7f4f');
