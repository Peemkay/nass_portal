-- Schema updates for student portal functionality

-- Create students table if it doesn't exist
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

-- Add password and account fields to students table
ALTER TABLE students ADD COLUMN password TEXT;
ALTER TABLE students ADD COLUMN email TEXT;
ALTER TABLE students ADD COLUMN phone TEXT;
ALTER TABLE students ADD COLUMN account_status TEXT DEFAULT 'active';
ALTER TABLE students ADD COLUMN last_login TIMESTAMP;
ALTER TABLE students ADD COLUMN reset_token TEXT;
ALTER TABLE students ADD COLUMN reset_token_expiry TIMESTAMP;
ALTER TABLE students ADD COLUMN is_portal_registered BOOLEAN DEFAULT 0;

-- Create table for student profile updates
CREATE TABLE IF NOT EXISTS student_profile_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    admin_id INTEGER,
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admins (id)
);

-- Create table for student notifications
CREATE TABLE IF NOT EXISTS student_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info', -- info, warning, success, error
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Create table for student login history
CREATE TABLE IF NOT EXISTS student_login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_student_notifications_student_id ON student_notifications(student_id);
CREATE INDEX IF NOT EXISTS idx_student_login_history_student_id ON student_login_history(student_id);
CREATE INDEX IF NOT EXISTS idx_student_profile_updates_student_id ON student_profile_updates(student_id);
