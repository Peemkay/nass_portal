DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS courses;

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

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
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
CREATE INDEX idx_students_service_number ON students(service_number);
CREATE INDEX idx_students_surname ON students(surname);
CREATE INDEX idx_students_rank ON students(rank);
CREATE INDEX idx_students_current_unit ON students(current_unit);
