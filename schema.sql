DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO admins (username, password) VALUES ('admin', 'password');  #  default admin user.  CHANGE THIS PASSWORD.
