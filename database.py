import telebot
import sqlite3
from datetime import datetime


def save_user(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            date_joined TEXT
        )
    """
    )

    cursor.execute(
        """
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, date_joined)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()
