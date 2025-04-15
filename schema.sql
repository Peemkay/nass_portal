DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS courses;

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_number TEXT NOT NULL,
    rank TEXT NOT NULL,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    dob TEXT NOT NULL,
    year_in_rank TEXT NOT NULL,
    year_of_last_promotion TEXT NOT NULL,
    nationality TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    state_of_origin TEXT NOT NULL,
    permanent_address TEXT NOT NULL,
    facebook TEXT,
    twitter TEXT,
    whatsapp TEXT,
    instagram TEXT,
    nok_name_1 TEXT NOT NULL,
    nok_address_1 TEXT NOT NULL,
    nok_gsm_number_1 TEXT NOT NULL,
    nok_email_1 TEXT,
    uni_serial TEXT,
    uni_name TEXT,
    uni_year_from TEXT,
    uni_year_to TEXT,
    uni_cert TEXT,
    uni_grade TEXT,
    uni_remarks TEXT,
    military_serial TEXT,
    military_name TEXT,
    military_year_from TEXT,
    military_year_to TEXT,
    military_cert TEXT,
    military_grade TEXT,
    military_remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    duration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_students_personnel_number ON students(personnel_number);
CREATE INDEX idx_students_name ON students(name);
CREATE INDEX idx_students_rank ON students(rank);
CREATE INDEX idx_students_unit ON students(unit);

-- Insert default admin user with hashed password
INSERT INTO admins (username, password)
VALUES ('admin', 'pbkdf2:sha256:260000$wgVnGBi0mZIkLHtJ$4e8d3f9ab8c6f936b8106c47e4f2a568f0e0c2c0a53a4e8c5f19b4d0e6f7c8d9');
