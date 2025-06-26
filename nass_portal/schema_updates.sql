-- Schema updates for the NASS Portal

-- Table for saving registration progress
CREATE TABLE IF NOT EXISTS registration_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_number TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    current_page INTEGER NOT NULL,
    session_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_number, date_of_birth)
);

-- Table for courses
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    level TEXT,
    department TEXT,
    duration INTEGER,
    start_date TEXT,
    end_date TEXT,
    registration_deadline TEXT,
    max_students INTEGER,
    is_active BOOLEAN DEFAULT 1,
    quarter TEXT,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for student course registrations
CREATE TABLE IF NOT EXISTS student_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT DEFAULT 'registered', -- registered, in_progress, completed, dropped
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TEXT,
    grade TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    UNIQUE(student_id, course_id)
);

-- Table for certificates
CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    certificate_file TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    certificate_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    UNIQUE(student_id, course_id)
);

-- Table for registration quarters
CREATE TABLE IF NOT EXISTS registration_quarters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    registration_deadline TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 0,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add corps column to students table if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS corps TEXT;

-- Add current_unit column to students table if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS current_unit TEXT;

-- Add date_of_commission column to students table if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS date_of_commission TEXT;

-- Add years_in_service column to students table if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS years_in_service INTEGER;

-- Add last_login column to students table if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create departments table if it doesn't exist
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Insert default departments if they don't exist
INSERT OR IGNORE INTO departments (name, description) VALUES
('CCD', 'Combat Communication Department'),
('ED', 'Engineering Department'),
('TSD', 'Technical System Department'),
('ICTD', 'Information and Communication Technology Department'),
('RDT&ED', 'Research Development Trial & Evaluation Department'),
('ATSA', 'Army Training Support Centre');

-- Create email_settings table if it doesn't exist
CREATE TABLE IF NOT EXISTS email_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    smtp_server TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    smtp_username TEXT NOT NULL,
    smtp_password TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert placeholder email settings if they don't exist
INSERT OR IGNORE INTO email_settings (
    smtp_server, smtp_port, smtp_username, smtp_password, sender_email, sender_name
) VALUES (
    'smtp.example.com', 587, 'email@example.com', 'your-password', 'noreply@example.com', 'Nigerian Army School of Signals'
);

-- Registration quarters and courses should be added through the admin interface
