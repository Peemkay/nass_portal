DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS courses;

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_number TEXT,
    rank TEXT,
    name TEXT NOT NULL,
    unit TEXT,
    dob TEXT,
    year_in_rank TEXT,
    year_of_last_promotion TEXT,
    nationality TEXT,
    marital_status TEXT,
    state_of_origin TEXT,
    permanent_address TEXT,
    facebook TEXT,
    twitter TEXT,
    whatsapp TEXT,
    instagram TEXT,
    nok_name_1 TEXT,
    nok_address_1 TEXT,
    nok_gsm_number_1 TEXT,
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
    course TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);


INSERT INTO admins (username, password) VALUES ('admin', 'password');  -- default admin user. CHANGE THIS PASSWORD.
