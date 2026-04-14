import sqlite3
import os

DB_PATH = './database/school.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Schema
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, department TEXT NOT NULL, year INTEGER NOT NULL, gpa REAL DEFAULT 0.0, status TEXT DEFAULT 'active', enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, department TEXT NOT NULL, credits INTEGER NOT NULL, instructor TEXT NOT NULL, capacity INTEGER DEFAULT 40, enrolled INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER REFERENCES students(id), course_id INTEGER REFERENCES courses(id), semester TEXT NOT NULL, grade TEXT DEFAULT NULL, enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(student_id, course_id, semester)
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER REFERENCES students(id), course_id INTEGER REFERENCES courses(id), semester TEXT NOT NULL, score REAL NOT NULL, letter_grade TEXT NOT NULL, remarks TEXT, graded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER REFERENCES users(id), action TEXT NOT NULL, details TEXT, ip_address TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS fee_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER REFERENCES students(id), amount REAL NOT NULL, due_date DATE NOT NULL, paid_date DATE, status TEXT DEFAULT 'pending', semester TEXT NOT NULL
        );
    """)

    # Check if seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [
            ('admin', 'admin123', 'admin'),
            ('john_doe', 'student123', 'student'),
            ('jane_smith', 'student123', 'student')
        ])

        students = [
            ('Alice Johnson', 'alice@school.edu', 'Computer Science', 2, 3.8, 'active'),
            ('Bob Martinez', 'bob@school.edu', 'Mathematics', 3, 3.2, 'active'),
            ('Carol Williams', 'carol@school.edu', 'Physics', 1, 3.9, 'active'),
        ]
        cursor.executemany("INSERT INTO students (name, email, department, year, gpa, status) VALUES (?, ?, ?, ?, ?, ?)", students)

        courses = [
            ('CS101', 'Intro to Programming', 'Computer Science', 3, 'Dr. Smith', 35, 32),
            ('MA101', 'Calculus I', 'Mathematics', 4, 'Dr. Brown', 40, 38),
        ]
        cursor.executemany("INSERT INTO courses (code, name, department, credits, instructor, capacity, enrolled) VALUES (?, ?, ?, ?, ?, ?, ?)", courses)

        conn.commit()
        print("✅ Database initialized and seeded successfully.")
    
    conn.close()