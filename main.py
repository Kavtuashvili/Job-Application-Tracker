import sqlite3
import hashlib
import csv

from datetime import datetime


DATABASE_NAME = "jobs.db"


# =========================================================
# DATABASE
# =========================================================

def connect_db():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = connect_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

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


# =========================================================
# VALIDATION HELPERS
# =========================================================

JOB_STATUSES = [
    "Applied",
    "Interview",
    "Rejected",
    "Accepted"
]

JOB_TYPES = [
    "Full-time",
    "Part-time",
    "Internship",
    "Freelance"
]

WORK_MODES = [
    "Remote",
    "On-site",
    "Hybrid"
]

INTERVIEW_TYPES = [
    "Online",
    "Phone",
    "In-person"
]

INTERVIEW_STATUSES = [
    "Scheduled",
    "Completed",
    "Cancelled"
]


def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


def get_valid_date(prompt, allow_empty=False, current_value=None):
    while True:
        value = input(prompt).strip()

        if allow_empty and not value:
            return current_value

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value

        except ValueError:
            print(
                "Invalid date. Please use YYYY-MM-DD."
            )


def get_valid_time(prompt, allow_empty=False, current_value=None):
    while True:
        value = input(prompt).strip()

        if allow_empty and not value:
            return current_value

        try:
            datetime.strptime(value, "%H:%M")
            return value

        except ValueError:
            print(
                "Invalid time. Please use HH:MM."
            )


def get_valid_salary(prompt, allow_empty=True, current_value=None):
    while True:
        value = input(prompt).strip()

        if not value:
            if allow_empty:
                return current_value

            print("Salary is required.")
            continue

        try:
            salary = float(value)

            if salary < 0:
                print("Salary cannot be negative.")
                continue

            return salary

        except ValueError:
            print("Invalid salary. Please enter a number.")


def get_valid_choice(prompt, options, allow_empty=False, current_value=None):
    print("\nAvailable options:")

    for option in options:
        print(f"- {option}")

    while True:
        value = input(prompt).strip()

        if allow_empty and not value:
            return current_value

        for option in options:
            if value.lower() == option.lower():
                return option

        print(
            "Invalid option. Please choose one of the listed options."
        )


def get_valid_id(prompt):
    while True:
        value = input(prompt).strip()

        try:
            number = int(value)

            if number <= 0:
                print("ID must be a positive number.")
                continue

            return number

        except ValueError:
            print("Invalid ID. Please enter a number.")


# =========================================================
# PASSWORD
# =========================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =========================================================
# REGISTER
# =========================================================

def register():
    print("\n================================")
    print("           REGISTER")
    print("================================")

    username = get_non_empty_input("Username: ")
    email = get_non_empty_input("Email: ")
    password = get_non_empty_input("Password: ")

    if len(password) < 6:
        print("\nPassword must contain at least 6 characters.")
        return

    hashed_password = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = connect_db()

    try:
        connection.execute(
            """
            INSERT INTO users
            (username, email, password, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password,
                created_at
            )
        )

        connection.commit()

        print("\nRegistration successful!")

    except sqlite3.IntegrityError:
        print("\nUsername or email already exists.")

    finally:
        connection.close()


# =========================================================
# LOGIN
# =========================================================

def login():
    print("\n================================")
    print("             LOGIN")
    print("================================")

    username = get_non_empty_input("Username: ")
    password = get_non_empty_input("Password: ")

    hashed_password = hash_password(password)

    connection = connect_db()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
        """,
        (
            username,
            hashed_password
        )
    ).fetchone()

    connection.close()

    if user:
        print(f"\nWelcome, {user['username']}!")
        return user

    print("\nInvalid username or password.")
    return None


# =========================================================
# ADD JOB
# =========================================================

def add_job(user):
    print("\n================================")
    print("            ADD JOB")
    print("================================")

    company = get_non_empty_input("Company: ")
    position = get_non_empty_input("Position: ")
    location = input("Location: ").strip()

    date_applied = get_valid_date(
        "Date Applied (YYYY-MM-DD): "
    )

    status = get_valid_choice(
        "Status: ",
        JOB_STATUSES
    )

    salary = get_valid_salary(
        "Salary (optional): "
    )

    job_type = get_valid_choice(
        "Job Type: ",
        JOB_TYPES
    )

    work_mode = get_valid_choice(
        "Work Mode: ",
        WORK_MODES
    )

    job_url = input("Job URL (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = connect_db()

    connection.execute(
        """
        INSERT INTO jobs (
            user_id,
            company,
            position,
            location,
            date_applied,
            status,
            salary,
            job_type,
            work_mode,
            job_url,
            notes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            company,
            position,
            location,
            date_applied,
            status,
            salary,
            job_type,
            work_mode,
            job_url,
            notes,
            created_at
        )
    )

    connection.commit()
    connection.close()

    print("\nJob application added successfully!")


# =========================================================
# VIEW JOBS
# =========================================================

def view_jobs(user):
    print("\n================================")
    print("          MY JOBS")
    print("================================")

    connection = connect_db()

    jobs = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE user_id = ?
        ORDER BY date_applied DESC, id DESC
        """,
        (user["id"],)
    ).fetchall()

    connection.close()

    if not jobs:
        print("\nYou don't have any job applications.")
        return

    for job in jobs:
        print("\n--------------------------------")
        print(f"ID: {job['id']}")
        print(f"Company: {job['company']}")
        print(f"Position: {job['position']}")
        print(f"Location: {job['location'] or 'N/A'}")
        print(f"Date Applied: {job['date_applied']}")
        print(f"Status: {job['status']}")
        print(
            f"Salary: "
            f"{job['salary'] if job['salary'] is not None else 'N/A'}"
        )
        print(f"Job Type: {job['job_type'] or 'N/A'}")
        print(f"Work Mode: {job['work_mode'] or 'N/A'}")
        print(f"URL: {job['job_url'] or 'N/A'}")
        print(f"Notes: {job['notes'] or 'N/A'}")


# =========================================================
# SEARCH JOBS
# =========================================================

def search_jobs(user):
    print("\n================================")
    print("         SEARCH JOBS")
    print("================================")

    keyword = get_non_empty_input(
        "Search company, position or location: "
    )

    connection = connect_db()

    jobs = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE user_id = ?
        AND (
            company LIKE ?
            OR position LIKE ?
            OR location LIKE ?
        )
        ORDER BY date_applied DESC
        """,
        (
            user["id"],
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        )
    ).fetchall()

    connection.close()

    if not jobs:
        print("\nNo matching jobs found.")
        return

    print(f"\nFound {len(jobs)} job(s):")

    for job in jobs:
        print("\n--------------------------------")
        print(f"ID: {job['id']}")
        print(f"Company: {job['company']}")
        print(f"Position: {job['position']}")
        print(f"Location: {job['location'] or 'N/A'}")
        print(f"Date Applied: {job['date_applied']}")
        print(f"Status: {job['status']}")


# =========================================================
# FILTER JOBS
# =========================================================

def filter_jobs(user):
    print("\n================================")
    print("       FILTER BY STATUS")
    print("================================")

    status = get_valid_choice(
        "Status: ",
        JOB_STATUSES
    )

    connection = connect_db()

    jobs = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE user_id = ?
        AND status = ?
        ORDER BY date_applied DESC
        """,
        (
            user["id"],
            status
        )
    ).fetchall()

    connection.close()

    if not jobs:
        print("\nNo jobs found with this status.")
        return

    print(f"\nFound {len(jobs)} job(s):")

    for job in jobs:
        print("\n--------------------------------")
        print(f"ID: {job['id']}")
        print(f"Company: {job['company']}")
        print(f"Position: {job['position']}")
        print(f"Date Applied: {job['date_applied']}")
        print(f"Status: {job['status']}")


# =========================================================
# UPDATE JOB
# =========================================================

def update_job(user):
    print("\n================================")
    print("          UPDATE JOB")
    print("================================")

    job_id = get_valid_id("Enter Job ID: ")

    connection = connect_db()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            user["id"]
        )
    ).fetchone()

    if not job:
        connection.close()
        print("\nJob not found.")
        return

    print("\nLeave a field empty to keep the current value.")

    company = input(
        f"Company [{job['company']}]: "
    ).strip()

    position = input(
        f"Position [{job['position']}]: "
    ).strip()

    location = input(
        f"Location [{job['location'] or ''}]: "
    ).strip()

    date_applied = get_valid_date(
        f"Date Applied [{job['date_applied']}]: ",
        allow_empty=True,
        current_value=job["date_applied"]
    )

    status = get_valid_choice(
        "Status: ",
        JOB_STATUSES,
        allow_empty=True,
        current_value=job["status"]
    )

    salary = get_valid_salary(
        f"Salary [{job['salary'] if job['salary'] is not None else ''}]: ",
        allow_empty=True,
        current_value=job["salary"]
    )

    job_type = get_valid_choice(
        "Job Type: ",
        JOB_TYPES,
        allow_empty=True,
        current_value=job["job_type"]
    )

    work_mode = get_valid_choice(
        "Work Mode: ",
        WORK_MODES,
        allow_empty=True,
        current_value=job["work_mode"]
    )

    job_url = input(
        f"Job URL [{job['job_url'] or ''}]: "
    ).strip()

    notes = input(
        f"Notes [{job['notes'] or ''}]: "
    ).strip()

    company = company or job["company"]
    position = position or job["position"]
    location = location or job["location"]
    job_url = job_url or job["job_url"]
    notes = notes or job["notes"]

    connection.execute(
        """
        UPDATE jobs
        SET
            company = ?,
            position = ?,
            location = ?,
            date_applied = ?,
            status = ?,
            salary = ?,
            job_type = ?,
            work_mode = ?,
            job_url = ?,
            notes = ?

        WHERE id = ?
        AND user_id = ?
        """,
        (
            company,
            position,
            location,
            date_applied,
            status,
            salary,
            job_type,
            work_mode,
            job_url,
            notes,
            job_id,
            user["id"]
        )
    )

    connection.commit()
    connection.close()

    print("\nJob updated successfully!")


# =========================================================
# DELETE JOB
# =========================================================

def delete_job(user):
    print("\n================================")
    print("           DELETE JOB")
    print("================================")

    job_id = get_valid_id("Enter Job ID: ")

    connection = connect_db()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            user["id"]
        )
    ).fetchone()

    if not job:
        connection.close()
        print("\nJob not found.")
        return

    print("\n--------------------------------")
    print(f"Company: {job['company']}")
    print(f"Position: {job['position']}")
    print(f"Status: {job['status']}")

    confirmation = input(
        "\nDelete this job? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        connection.execute(
            """
            DELETE FROM jobs
            WHERE id = ?
            AND user_id = ?
            """,
            (
                job_id,
                user["id"]
            )
        )

        connection.commit()

        print("\nJob deleted successfully!")

    else:
        print("\nDeletion cancelled.")

    connection.close()


# =========================================================
# STATISTICS
# =========================================================

def statistics(user):
    print("\n================================")
    print("           STATISTICS")
    print("================================")

    connection = connect_db()

    job_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total,

            SUM(
                CASE
                    WHEN status = 'Applied'
                    THEN 1 ELSE 0
                END
            ) AS applied,

            SUM(
                CASE
                    WHEN status = 'Interview'
                    THEN 1 ELSE 0
                END
            ) AS interview,

            SUM(
                CASE
                    WHEN status = 'Rejected'
                    THEN 1 ELSE 0
                END
            ) AS rejected,

            SUM(
                CASE
                    WHEN status = 'Accepted'
                    THEN 1 ELSE 0
                END
            ) AS accepted,

            AVG(
                CASE
                    WHEN salary IS NOT NULL
                    AND salary > 0
                    THEN salary
                END
            ) AS average_salary

        FROM jobs

        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    interview_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_interviews,

            SUM(
                CASE
                    WHEN status = 'Scheduled'
                    THEN 1 ELSE 0
                END
            ) AS scheduled,

            SUM(
                CASE
                    WHEN status = 'Completed'
                    THEN 1 ELSE 0
                END
            ) AS completed,

            SUM(
                CASE
                    WHEN status = 'Cancelled'
                    THEN 1 ELSE 0
                END
            ) AS cancelled

        FROM interviews

        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    today = datetime.now().strftime("%Y-%m-%d")

    upcoming = connection.execute(
        """
        SELECT COUNT(*)
        FROM interviews

        WHERE user_id = ?
        AND interview_date >= ?
        AND status = 'Scheduled'
        """,
        (
            user["id"],
            today
        )
    ).fetchone()[0]

    connection.close()

    total = job_stats["total"] or 0
    applied = job_stats["applied"] or 0
    interview = job_stats["interview"] or 0
    rejected = job_stats["rejected"] or 0
    accepted = job_stats["accepted"] or 0

    average_salary = job_stats["average_salary"]

    total_interviews = (
        interview_stats["total_interviews"] or 0
    )

    scheduled = interview_stats["scheduled"] or 0
    completed = interview_stats["completed"] or 0
    cancelled = interview_stats["cancelled"] or 0

    interview_rate = 0
    acceptance_rate = 0

    if total > 0:
        interview_rate = (
            interview / total
        ) * 100

        acceptance_rate = (
            accepted / total
        ) * 100

    print("\n--------------------------------")
    print("JOB APPLICATIONS")
    print("--------------------------------")

    print(f"Total Applications: {total}")
    print(f"Applied: {applied}")
    print(f"Interview: {interview}")
    print(f"Rejected: {rejected}")
    print(f"Accepted: {accepted}")

    if average_salary is not None:
        print(
            f"Average Salary: "
            f"{average_salary:.2f}"
        )
    else:
        print("Average Salary: N/A")

    print(
        f"Interview Rate: "
        f"{interview_rate:.2f}%"
    )

    print(
        f"Acceptance Rate: "
        f"{acceptance_rate:.2f}%"
    )

    print("\n--------------------------------")
    print("INTERVIEWS")
    print("--------------------------------")

    print(
        f"Total Interviews: "
        f"{total_interviews}"
    )

    print(f"Scheduled: {scheduled}")
    print(f"Upcoming: {upcoming}")
    print(f"Completed: {completed}")
    print(f"Cancelled: {cancelled}")


# =========================================================
# ADD INTERVIEW
# =========================================================

def add_interview(user):
    print("\n================================")
    print("          ADD INTERVIEW")
    print("================================")

    connection = connect_db()

    jobs = connection.execute(
        """
        SELECT id, company, position
        FROM jobs

        WHERE user_id = ?

        ORDER BY id DESC
        """,
        (user["id"],)
    ).fetchall()

    if not jobs:
        connection.close()

        print(
            "\nYou need to add a job first."
        )

        return

    print("\nYour Jobs:")

    for job in jobs:
        print(
            f"{job['id']}. "
            f"{job['company']} - "
            f"{job['position']}"
        )

    job_id = get_valid_id(
        "\nEnter Job ID: "
    )

    job = connection.execute(
        """
        SELECT *
        FROM jobs

        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            user["id"]
        )
    ).fetchone()

    if not job:
        connection.close()

        print("\nJob not found.")

        return

    interview_date = get_valid_date(
        "Interview Date (YYYY-MM-DD): "
    )

    interview_time = get_valid_time(
        "Interview Time (HH:MM): "
    )

    interview_type = get_valid_choice(
        "Interview Type: ",
        INTERVIEW_TYPES
    )

    status = get_valid_choice(
        "Status: ",
        INTERVIEW_STATUSES
    )

    notes = input(
        "Notes (optional): "
    ).strip()

    connection.execute(
        """
        INSERT INTO interviews (
            user_id,
            job_id,
            interview_date,
            interview_time,
            interview_type,
            status,
            notes
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            job_id,
            interview_date,
            interview_time,
            interview_type,
            status,
            notes
        )
    )

    connection.commit()
    connection.close()

    print("\nInterview added successfully!")


# =========================================================
# VIEW UPCOMING INTERVIEWS
# =========================================================

def view_upcoming_interviews(user):
    print("\n================================")
    print("       UPCOMING INTERVIEWS")
    print("================================")

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    connection = connect_db()

    interviews = connection.execute(
        """
        SELECT
            interviews.*,
            jobs.company,
            jobs.position

        FROM interviews

        JOIN jobs
            ON interviews.job_id = jobs.id

        WHERE interviews.user_id = ?
        AND interviews.interview_date >= ?
        AND interviews.status = 'Scheduled'

        ORDER BY
            interviews.interview_date ASC,
            interviews.interview_time ASC
        """,
        (
            user["id"],
            today
        )
    ).fetchall()

    connection.close()

    if not interviews:
        print("\nNo upcoming interviews.")
        return

    for interview in interviews:

        print("\n--------------------------------")
        print(
            f"Interview ID: "
            f"{interview['id']}"
        )

        print(
            f"Company: "
            f"{interview['company']}"
        )

        print(
            f"Position: "
            f"{interview['position']}"
        )

        print(
            f"Date: "
            f"{interview['interview_date']}"
        )

        print(
            f"Time: "
            f"{interview['interview_time']}"
        )

        print(
            f"Type: "
            f"{interview['interview_type']}"
        )

        print(
            f"Status: "
            f"{interview['status']}"
        )

        print(
            f"Notes: "
            f"{interview['notes'] or 'N/A'}"
        )


# =========================================================
# VIEW ALL INTERVIEWS
# =========================================================

def view_all_interviews(user):
    print("\n================================")
    print("          ALL INTERVIEWS")
    print("================================")

    connection = connect_db()

    interviews = connection.execute(
        """
        SELECT
            interviews.*,
            jobs.company,
            jobs.position

        FROM interviews

        JOIN jobs
            ON interviews.job_id = jobs.id

        WHERE interviews.user_id = ?

        ORDER BY
            interviews.interview_date DESC,
            interviews.interview_time DESC
        """,
        (user["id"],)
    ).fetchall()

    connection.close()

    if not interviews:
        print("\nNo interviews found.")
        return

    for interview in interviews:

        print("\n--------------------------------")
        print(
            f"Interview ID: "
            f"{interview['id']}"
        )

        print(
            f"Company: "
            f"{interview['company']}"
        )

        print(
            f"Position: "
            f"{interview['position']}"
        )

        print(
            f"Date: "
            f"{interview['interview_date']}"
        )

        print(
            f"Time: "
            f"{interview['interview_time']}"
        )

        print(
            f"Type: "
            f"{interview['interview_type']}"
        )

        print(
            f"Status: "
            f"{interview['status']}"
        )

        print(
            f"Notes: "
            f"{interview['notes'] or 'N/A'}"
        )


# =========================================================
# UPDATE INTERVIEW
# =========================================================

def update_interview(user):
    print("\n================================")
    print("        UPDATE INTERVIEW")
    print("================================")

    interview_id = get_valid_id(
        "Enter Interview ID: "
    )

    connection = connect_db()

    interview = connection.execute(
        """
        SELECT *
        FROM interviews

        WHERE id = ?
        AND user_id = ?
        """,
        (
            interview_id,
            user["id"]
        )
    ).fetchone()

    if not interview:
        connection.close()

        print("\nInterview not found.")

        return

    print(
        "\nLeave a field empty "
        "to keep the current value."
    )

    interview_date = get_valid_date(
        f"Date [{interview['interview_date']}]: ",
        allow_empty=True,
        current_value=interview["interview_date"]
    )

    interview_time = get_valid_time(
        f"Time [{interview['interview_time']}]: ",
        allow_empty=True,
        current_value=interview["interview_time"]
    )

    interview_type = get_valid_choice(
        "Interview Type: ",
        INTERVIEW_TYPES,
        allow_empty=True,
        current_value=interview["interview_type"]
    )

    status = get_valid_choice(
        "Status: ",
        INTERVIEW_STATUSES,
        allow_empty=True,
        current_value=interview["status"]
    )

    notes = input(
        f"Notes [{interview['notes'] or ''}]: "
    ).strip()

    notes = notes or interview["notes"]

    connection.execute(
        """
        UPDATE interviews

        SET
            interview_date = ?,
            interview_time = ?,
            interview_type = ?,
            status = ?,
            notes = ?

        WHERE id = ?
        AND user_id = ?
        """,
        (
            interview_date,
            interview_time,
            interview_type,
            status,
            notes,
            interview_id,
            user["id"]
        )
    )

    connection.commit()
    connection.close()

    print("\nInterview updated successfully!")


# =========================================================
# DELETE INTERVIEW
# =========================================================

def delete_interview(user):
    print("\n================================")
    print("        DELETE INTERVIEW")
    print("================================")

    interview_id = get_valid_id(
        "Enter Interview ID: "
    )

    connection = connect_db()

    interview = connection.execute(
        """
        SELECT
            interviews.*,
            jobs.company,
            jobs.position

        FROM interviews

        JOIN jobs
            ON interviews.job_id = jobs.id

        WHERE interviews.id = ?
        AND interviews.user_id = ?
        """,
        (
            interview_id,
            user["id"]
        )
    ).fetchone()

    if not interview:
        connection.close()

        print("\nInterview not found.")

        return

    print("\n--------------------------------")

    print(
        f"Company: "
        f"{interview['company']}"
    )

    print(
        f"Position: "
        f"{interview['position']}"
    )

    print(
        f"Date: "
        f"{interview['interview_date']}"
    )

    print(
        f"Time: "
        f"{interview['interview_time']}"
    )

    print(
        f"Status: "
        f"{interview['status']}"
    )

    confirmation = input(
        "\nDelete this interview? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        connection.execute(
            """
            DELETE FROM interviews

            WHERE id = ?
            AND user_id = ?
            """,
            (
                interview_id,
                user["id"]
            )
        )

        connection.commit()

        print(
            "\nInterview deleted successfully!"
        )

    else:
        print("\nDeletion cancelled.")

    connection.close()


# =========================================================
# INTERVIEWS MENU
# =========================================================

def interviews_menu(user):

    while True:

        print("\n================================")
        print("          INTERVIEWS")
        print("================================")

        print("1. Add Interview")
        print("2. View Upcoming Interviews")
        print("3. View All Interviews")
        print("4. Update Interview")
        print("5. Delete Interview")
        print("6. Back")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            add_interview(user)

        elif choice == "2":
            view_upcoming_interviews(user)

        elif choice == "3":
            view_all_interviews(user)

        elif choice == "4":
            update_interview(user)

        elif choice == "5":
            delete_interview(user)

        elif choice == "6":
            break

        else:
            print("\nInvalid option.")


# =========================================================
# EXPORT APPLICATIONS TO CSV
# =========================================================

def export_applications(user):
    print("\n================================")
    print("       EXPORT APPLICATIONS")
    print("================================")

    connection = connect_db()

    jobs = connection.execute(
        """
        SELECT
            company,
            position,
            location,
            date_applied,
            status,
            salary,
            job_type,
            work_mode,
            job_url,
            notes

        FROM jobs

        WHERE user_id = ?

        ORDER BY
            date_applied DESC,
            id DESC
        """,
        (user["id"],)
    ).fetchall()

    connection.close()

    if not jobs:
        print(
            "\nYou don't have any "
            "job applications to export."
        )

        return

    safe_username = "".join(
        char
        if char.isalnum() or char in ("_", "-")
        else "_"
        for char in user["username"]
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"job_applications_"
        f"{safe_username}_"
        f"{timestamp}.csv"
    )

    try:

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Company",
                "Position",
                "Location",
                "Date Applied",
                "Status",
                "Salary",
                "Job Type",
                "Work Mode",
                "Job URL",
                "Notes"
            ])

            for job in jobs:

                writer.writerow([
                    job["company"],
                    job["position"],
                    job["location"],
                    job["date_applied"],
                    job["status"],
                    job["salary"],
                    job["job_type"],
                    job["work_mode"],
                    job["job_url"],
                    job["notes"]
                ])

        print(
            "\nApplications exported successfully!"
        )

        print(
            f"File: {filename}"
        )

        print(
            f"Records exported: {len(jobs)}"
        )

    except OSError as error:

        print(
            f"\nCould not create export file: "
            f"{error}"
        )


# =========================================================
# USER MENU
# =========================================================

def user_menu(user):

    while True:

        print("\n================================")
        print("          JOB TRACKER")
        print("================================")

        print("1. Add Job")
        print("2. View My Jobs")
        print("3. Search Jobs")
        print("4. Filter by Status")
        print("5. Update Job")
        print("6. Delete Job")
        print("7. Statistics")
        print("8. Interviews")
        print("9. Logout")
        print("10. Export Applications")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            add_job(user)

        elif choice == "2":
            view_jobs(user)

        elif choice == "3":
            search_jobs(user)

        elif choice == "4":
            filter_jobs(user)

        elif choice == "5":
            update_job(user)

        elif choice == "6":
            delete_job(user)

        elif choice == "7":
            statistics(user)

        elif choice == "8":
            interviews_menu(user)

        elif choice == "9":
            print(
                "\nLogged out successfully."
            )
            break

        elif choice == "10":
            export_applications(user)

        else:
            print("\nInvalid option.")


# =========================================================
# MAIN MENU
# =========================================================

def main():

    create_tables()

    while True:

        print("\n================================")
        print("        JOB APPLICATION")
        print("             TRACKER")
        print("================================")

        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            register()

        elif choice == "2":

            user = login()

            if user:
                user_menu(user)

        elif choice == "3":

            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option.")




if __name__ == "__main__":
    main()