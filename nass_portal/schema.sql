DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS registration_periods;

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_number TEXT NOT NULL,
    rank TEXT NOT NULL,
    surname TEXT NOT NULL,
    other_names TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT NOT NULL,
    current_unit TEXT NOT NULL,
    date_of_commission TEXT NOT NULL,
    years_in_service INTEGER NOT NULL,
    passport_photo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    duration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_students_service_number ON students(service_number);
CREATE INDEX idx_students_surname ON students(surname);
CREATE INDEX idx_students_rank ON students(rank);
CREATE INDEX idx_students_current_unit ON students(current_unit);

-- Create registration_periods table for managing registration deadlines
CREATE TABLE registration_periods (
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

-- Insert default admin user with hashed password (password: admin123)
INSERT INTO admins (username, password)
VALUES ('admin', 'pbkdf2:sha256:150000$LnrTXNNj$d119fae74dc2817dd7c3c5bd9a27ebf2c1a7a5b237b0ecdd2c2a1e906c4c7f4f');
