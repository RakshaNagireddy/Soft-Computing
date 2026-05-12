import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "study_planner.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            name       TEXT NOT NULL,
            difficulty REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS study_plans (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            subject  TEXT NOT NULL,
            priority REAL NOT NULL,
            hours    REAL NOT NULL,
            plan     TEXT,
            date     TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")


def get_or_create_user(name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        user_id = row["id"]
    else:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return user_id


def save_subject(user_id: int, name: str, difficulty: float) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (user_id, name, difficulty) VALUES (?, ?, ?)",
        (user_id, name, difficulty),
    )
    conn.commit()
    subject_id = cursor.lastrowid
    conn.close()
    return subject_id


def save_study_plan(
    user_id: int,
    subject: str,
    priority: float,
    hours: float,
    plan: str,
    date: str,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO study_plans (user_id, subject, priority, hours, plan, date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, subject, priority, hours, plan, date),
    )
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def fetch_all_plans(user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            "SELECT * FROM study_plans WHERE user_id = ? ORDER BY date DESC",
            (user_id,),
        )
    else:
        cursor.execute("SELECT * FROM study_plans ORDER BY date DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_study_plan(plan_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()
