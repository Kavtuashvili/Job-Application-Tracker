import sqlite3


DATABASE_NAME = "jobs.db"


def connect_db():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = connect_db()

    
    # USERS TABLE
   

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    
    # JOBS TABLE
   

    connection.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            location TEXT,
            date_applied TEXT NOT NULL,
            status TEXT NOT NULL,
            salary REAL,
            job_type TEXT,
            work_mode TEXT,
            job_url TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    
    # INTERVIEWS TABLE
  
    connection.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            interview_date TEXT NOT NULL,
            interview_time TEXT NOT NULL,
            interview_type TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE,

            FOREIGN KEY (job_id)
            REFERENCES jobs(id)
            ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()
